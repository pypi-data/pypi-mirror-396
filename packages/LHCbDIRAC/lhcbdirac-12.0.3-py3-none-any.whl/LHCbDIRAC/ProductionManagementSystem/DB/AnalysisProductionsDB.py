###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Database class for storing information about Analysis Productions

For more information on the meaning of the various objects see :py:mod:`.AnalysisProductionsClient`.

Tables are defined using SQLAlchemy and imported from :py:mod:`.AnalysisProductionsObjects`.
Example usage of this class can be found in `Test_AnalysisProductionsDB.py`.
"""
import functools
import datetime
from collections import defaultdict
from copy import deepcopy
from contextlib import contextmanager
from urllib.parse import quote_plus

import threading

import pandas as pd
from cachetools import TTLCache, cached

from sqlalchemy import create_engine, delete, func, insert, or_, text, tuple_, select, case, JSON, cast, Integer, and_
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session

from DIRAC.ConfigurationSystem.Client.Utilities import getDBParameters
from DIRAC.Core.Base.DIRACDB import DIRACDB
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise

from LHCbDIRAC.ProductionManagementSystem.DB.AnalysisProductionsObjects import (
    ActionsInputModel,
    Base,
    AnalysisSample as AP,
    AutoTag,
    Tag,
    Request,
    AnalysisOwner,
    Publication,
    User,
)
from LHCbDIRAC.ProductionManagementSystem.DB.extra_func import json_group_array, json_group_object, json_length
from LHCbDIRAC.ProductionManagementSystem.Utilities.CSLookup import cern_username_to_person_id


# Reusable JSON expressions for common operations
class JSONHelpers:
    """Helper class for commonly used JSON SQL expressions"""

    @staticmethod
    def get_transformations():
        """Get the transformations array from extra_info"""
        return func.JSON_EXTRACT(AP.extra_info, "$.transformations")

    @staticmethod
    def get_last_transform_id():
        """Get the ID of the last transformation"""
        transformations_expr = JSONHelpers.get_transformations()
        return func.JSON_EXTRACT(
            AP.extra_info,
            func.concat(  # pylint: disable=not-callable
                "$.transformations[", json_length(transformations_expr) - 1, "].id"
            ),
        )

    @staticmethod
    def has_transformations():
        """Check if transformations array exists and is non-empty"""
        transformations_expr = JSONHelpers.get_transformations()
        return and_(
            func.JSON_TYPE(transformations_expr) == "ARRAY",
            json_length(transformations_expr) > 0,
        )


def inject_session(func):
    """Decorator to inject the session into a class method

    Decorator to start a SQLAlchemy Session and inject it in the wrapped function
    as a keyword argument.
    """

    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        if "session" in kwargs:
            raise NotImplementedError("session cannot be passed through the inject_session decorator")
        with self.session as session:
            return func(self, *args, **kwargs, session=session)

    return new_func


@cached(cache=TTLCache(maxsize=1, ttl=3600), lock=threading.Lock())
def storage_statistics():
    def filter(df):
        df.production = df.production.astype(int)
        df = df[df["SEName"] == "FakeSE"]
        df = df[df["production"] >= 0]
        return df

    # pop in a dataframe
    with pd.read_csv(
        "https://lhcbdirac.s3.cern.ch/storage-usage/storage.csv.zst",  # Hardcoded!
        iterator=True,
        compression="zstd",
        chunksize=2048,
    ) as reader:
        # fill histograms / aggregated stats
        prod_id_storage = (
            pd.concat(filter(df)[["production", "SESize", "filetype"]] for df in reader)
            .groupby(["production", "filetype"])
            .sum()
        )
    return prod_id_storage.SESize.to_dict()


class AnalysisProductionsDB(DIRACDB):
    __engineCache = {}

    def __init__(self, *, url=None, parentLogger=None):
        self.fullname = self.__class__.__name__
        super().__init__(parentLogger=parentLogger)
        if url is None:
            param = returnValueOrRaise(getDBParameters("ProductionManagement/AnalysisProductionsDB"))
            param["Password"] = quote_plus(param["Password"])
            url = f"mysql://{param['User']}:{param['Password']}@{param['Host']}:{param['Port']}/{param['DBName']}"
        self.setURL(url)

    def setURL(self, url):
        if url not in self.__engineCache or ":memory:" in url:
            engine = create_engine(
                url,
                pool_recycle=3600,
                echo_pool=True,
                echo=self.log.getLevel() == "DEBUG",
                future=True,
            )
            Base.metadata.create_all(engine)
            self.__engineCache[url] = engine
        self.engine = self.__engineCache[url]

    @property
    @contextmanager
    def session(self):
        with Session(self.engine, future=True) as session, session.begin():
            # NOTE: SESSION ONLY! THIS WILL NOT SET THE SERVER TIMEZONE
            # Only set timezone for MySQL (SQLite doesn't support timezones)
            if self.engine.dialect.name == "mysql":
                session.execute(text('SET @@session.time_zone = "+00:00";'))
            yield session

    @inject_session
    def listAnalyses(self, *, at_time=None, session: Session):
        query = select(AP.wg, AP.analysis).distinct()
        query = _filterForTime(query, AP, at_time)
        result = defaultdict(list)
        for wg, analysis in session.execute(query):
            result[wg].append(analysis)
        return dict(result)

    @inject_session
    def listAnalyses2(self, *, at_time=None, session: Session):
        # Create owners subquery for efficient joining later with temporal filtering
        if at_time is None:
            at_time = func.now()  # pylint: disable=not-callable

        owners_subquery = (
            select(
                AnalysisOwner.wg,
                AnalysisOwner.analysis,
                json_group_array(AnalysisOwner.username).label("owner_usernames"),
            )
            .where(
                and_(
                    AnalysisOwner.validity_start <= at_time,
                    or_(AnalysisOwner.validity_end.is_(None), AnalysisOwner.validity_end > at_time),
                )
            )
            .group_by(AnalysisOwner.wg, AnalysisOwner.analysis)
            .subquery()
        )

        # Build an expression that extracts the last transform_id from the JSON array,
        # but only if the "transformations" value is an array with at least one element.
        last_transform_expr = case(
            (
                JSONHelpers.has_transformations(),
                # If so, produce a JSON array (ft, sample_id, trf_id).
                func.JSON_ARRAY(
                    AP.filetype,
                    AP.sample_id,
                    JSONHelpers.get_last_transform_id(),
                    AP.request_id,
                ),
            ),
            else_=None,  # yield NULL when the conditions aren’t met.
        )
        # Then, wrap the aggregate in a COALESCE so that if JSON_ARRAYAGG returns NULL,
        # it will instead return an empty JSON array (via MySQL’s JSON_ARRAY()).
        transform_ids_agg = func.COALESCE(json_group_array(last_transform_expr), func.JSON_ARRAY()).label(
            "transform_ids"
        )

        # Select the analyses and build the list of results with owners joined
        query = select(
            AP.wg,
            AP.analysis,
            # Add a column n_{STATE_NAME} containing the number of analyses in each possible state
            *(
                # MySQL returns a decimal type from sum() so we need to cast it to an integer
                cast(func.sum(case((AP.state == state, 1), else_=0)), Integer).label(  # pylint: disable=not-callable
                    f"n_{state}"
                )
                for state in AP.VALID_STATES
            ),
            func.count().label("n_total"),  # pylint: disable=not-callable
            func.min(AP.housekeeping_interaction_due).label("earliest_housekeeping_due"),
            transform_ids_agg,
            func.COALESCE(owners_subquery.c.owner_usernames, func.JSON_ARRAY()).label("owners"),
        )
        query = query.outerjoin(
            owners_subquery, and_(AP.wg == owners_subquery.c.wg, AP.analysis == owners_subquery.c.analysis)
        )
        query = query.group_by(AP.wg, AP.analysis)
        query = _filterForTime(query, AP, at_time)

        storage_metadata_dict = storage_statistics()
        return [
            dict(row._mapping)
            | {"owners": list(row.owners or [])}
            | {
                "transform_ids": (
                    [
                        {
                            "filetype": o[0],
                            "sample_id": o[1],
                            "transform_id": o[2],
                            "storage_use": storage_metadata_dict.get(
                                (
                                    o[2],
                                    o[0],
                                ),
                                0,
                            ),
                        }
                        for o in row.transform_ids
                        if o
                    ]
                ),
            }
            for row in session.execute(query).all()
        ]

    @inject_session
    def listRequests(self, *, session: Session):
        analyses = select(
            AP.request_id,
            AP.filetype,
            AP.name,
            AP.version,
            json_group_array(func.json_array(AP.wg, AP.analysis)).label("analyses"),
        )
        analyses = analyses.group_by(AP.request_id, AP.filetype, AP.name, AP.version)
        analyses = _filterForTime(analyses, AP, at_time=None)
        analyses = analyses.subquery(name="requests")

        autotags = select(
            Request.request_id,
            Request.filetype,
            # Can't use AGG_FUNC.filter as it's not supported by mysql
            case(
                (
                    func.sum(AutoTag.name.is_not(None)) == 0,  # pylint: disable=not-callable
                    func.json_object(type_=JSON),  # pylint: disable=not-callable
                ),
                else_=json_group_object(AutoTag.name, AutoTag.value),
            ).label("autotags"),
        )
        autotags = autotags.join(
            AutoTag,
            tuple_(Request.request_id, Request.filetype) == tuple_(AutoTag.request_id, AutoTag.filetype),
            isouter=True,
        )
        autotags = autotags.group_by(Request.request_id, Request.filetype)
        autotags = autotags.subquery(name="autotags")

        tags = select(
            AP.request_id,
            AP.filetype,
            # Can't use AGG_FUNC.filter as it's not supported by mysql
            case(
                (
                    func.sum(Tag.name.is_not(None)) == 0,  # pylint: disable=not-callable
                    func.json_array(type_=JSON),  # pylint: disable=not-callable
                ),
                else_=json_group_array(func.json_array(Tag.name, Tag.value)),
            ).label("tags"),
        ).distinct()
        tags = tags.join(Tag, AP.sample_id == Tag.sample_id, isouter=True)
        tags = tags.group_by(AP.request_id, AP.filetype)
        tags = tags.subquery(name="tags")

        query = select(analyses, autotags.c.autotags, tags.c.tags)
        query = query.join(
            autotags,
            tuple_(analyses.c.request_id, analyses.c.filetype) == tuple_(autotags.c.request_id, autotags.c.filetype),
            isouter=True,
        )
        query = query.join(
            tags,
            tuple_(analyses.c.request_id, analyses.c.filetype) == tuple_(tags.c.request_id, tags.c.filetype),
            isouter=True,
        )
        return [dict(row._mapping) for row in session.execute(query).all()]

    @inject_session
    def getOwners(self, *, wg=None, analysis=None, at_time=None, session: Session):
        """Get owners for an analysis at a specific time (defaults to current time)"""
        query = select(AnalysisOwner.username)
        query = query.where(AnalysisOwner.wg == wg)
        query = query.where(AnalysisOwner.analysis == analysis)

        # Apply temporal filtering
        query = _filterForTime(query, AnalysisOwner, at_time)

        return session.execute(query).scalars().all()

    @inject_session
    def getOwnershipHistory(self, *, wg=None, analysis=None, session: Session):
        """Get complete ownership history for an analysis"""
        query = (
            select(
                AnalysisOwner.username,
                AnalysisOwner.validity_start,
                AnalysisOwner.validity_end,
                AnalysisOwner.created_at,
            )
            .where(and_(AnalysisOwner.wg == wg, AnalysisOwner.analysis == analysis))
            .order_by(AnalysisOwner.validity_start.desc())
        )

        return [dict(row._mapping) for row in session.execute(query).all()]

    @inject_session
    def getUsers(self, *, username: str | None = None, session: Session):
        if username is not None:
            username = username.lower()
            # Enforce lower name a-z0-9 usernames i.e. no emails
            if not username.isalnum():
                raise ValueError(f"Invalid username {username}")
        query = select(User)
        if username is not None:
            query = query.where(User.username == username)
        return [user.toDict() for user in session.execute(query).scalars()]

    @inject_session
    def updateUsers(self, *, users: list[dict], session: Session):
        if not users:
            return

        # Validate all users first before any updates
        processed_users = []
        existing_usernames = set()

        for user in users:
            if "username" not in user:
                raise ValueError("username is required to update a user")
            username = user["username"].lower()
            # Enforce lower name a-z0-9 usernames i.e. no emails
            if not username.isalnum():
                raise ValueError(f"Invalid username {username}")
            existing_usernames.add(username)

            # Process and validate the user data
            processed_user = {"username": username}
            for key, value in user.items():
                if key == "username":
                    continue
                if not hasattr(User, key):
                    raise ValueError(f"User has no attribute {key}")

                # Convert ISO datetime strings to datetime objects for datetime fields
                if key in ("active_since", "active_until", "accepted_agreement") and isinstance(value, str):
                    try:
                        value = datetime.datetime.fromisoformat(value)
                    except ValueError as e:
                        raise ValueError(f"Invalid datetime format for {key}: {value}") from e

                processed_user[key] = value
            processed_users.append(processed_user)

        # Check all users exist in database
        existing_in_db = set(
            session.execute(select(User.username).where(User.username.in_(existing_usernames))).scalars().all()
        )
        missing_users = existing_usernames - existing_in_db
        if missing_users:
            raise ValueError(f"Users do not exist in the database: {missing_users}")

        # Perform bulk update using SQLAlchemy's bulk_update_mappings
        if processed_users:
            session.bulk_update_mappings(User, processed_users)

    @inject_session
    def setOwners(self, *, wg=None, analysis=None, owners=None, enforce_ccid=True, session: Session):
        """Set owners for an analysis with temporal versioning support"""
        owners = [owner.lower() for owner in owners]
        # Enforce lower name a-z0-9 usernames i.e. no emails
        for owner in owners:
            if not owner.isalnum():
                raise ValueError(f"Invalid username {owner}")

        # Get all existing usernames in one query
        existing_usernames = set(
            session.execute(select(User.username).where(User.username.in_(owners))).scalars().all()
        )
        new_users = [
            {"username": owner, "person_id": cern_username_to_person_id(owner)}
            for owner in owners
            if owner not in existing_usernames
        ]
        if enforce_ccid:
            # Raise exception if any owner does not have a person_id
            # Check for users without valid CERN person IDs
            invalid_users = [user["username"] for user in new_users if user["person_id"] is None]
            if invalid_users:
                raise ValueError(
                    "The following owners do not have valid Person IDs in the CS:"
                    f" {', '.join(invalid_users)}."
                    " Service accounts or e-groups are not valid."
                )

        # Insert only the ones that don't exist
        if new_users:
            session.execute(
                User.__table__.insert(),
                new_users,
            )

        # Get current owners (those with active validity periods)
        current_time = func.now()  # pylint: disable=not-callable
        current_owners_query = select(AnalysisOwner.username).where(
            and_(
                AnalysisOwner.wg == wg,
                AnalysisOwner.analysis == analysis,
                AnalysisOwner.validity_start <= current_time,
                or_(AnalysisOwner.validity_end.is_(None), AnalysisOwner.validity_end > current_time),
            )
        )
        current_owners = set(session.execute(current_owners_query).scalars().all())
        new_owners_set = set(owners)

        # If ownership is unchanged, do nothing
        if current_owners == new_owners_set:
            return

        # Calculate which owners to remove and which to add
        owners_to_remove = current_owners - new_owners_set
        owners_to_add = new_owners_set - current_owners

        # End validity only for owners that are being removed
        if owners_to_remove:
            session.execute(
                AnalysisOwner.__table__.update()
                .where(
                    and_(
                        AnalysisOwner.wg == wg,
                        AnalysisOwner.analysis == analysis,
                        AnalysisOwner.username.in_(owners_to_remove),
                        AnalysisOwner.validity_end.is_(None),
                    )
                )
                .values(validity_end=current_time)
            )

        # Insert new ownership records only for new owners
        if owners_to_add:
            new_ownership_records = [
                {
                    "wg": wg,
                    "analysis": analysis,
                    "username": owner,
                }
                for owner in owners_to_add
            ]
            session.execute(AnalysisOwner.__table__.insert(), new_ownership_records)

    @inject_session
    def getProductions(
        self,
        *,
        wg=None,
        analysis=None,
        version=None,
        name=None,
        state=None,
        at_time=None,
        show_archived=False,
        require_has_publication=False,
        session: Session,
    ):
        query = select(
            AP.wg,
            AP.analysis,
            AP.sample_id,
            AP.validity_start,
            AP.validity_end,
            AP.name,
            AP.version,
            AP.request_id,
            AP.filetype,
            AP.state,
            AP.last_state_update,
            AP.extra_info["transformations"].label("transformations"),
            AP.progress,
            AP.extra_info["jira_task"].label("jira_task"),
            AP.extra_info["merge_request"].label("merge_request"),
            AP.housekeeping_interaction_due,
        )
        query = query.filter(*_buildCondition(wg, analysis, name, version))
        if state is not None:
            query = query.filter(AP.state == state)
        if not show_archived:
            query = _filterForTime(query, AP, at_time)

        query = query.group_by(AP.sample_id).subquery(name="samples")

        pub_q = select(
            Publication.sample_id,
            case(
                (
                    func.count(Publication.number) == 0,  # pylint: disable=not-callable
                    func.json_array(type_=JSON),  # pylint: disable=not-callable
                ),
                else_=json_group_array(Publication.number),
            ).label("publications"),
        )
        pub_q = pub_q.group_by(Publication.sample_id).subquery(name="pubs")

        mque = select(query, pub_q.c.publications)
        mque = mque.join(pub_q, pub_q.c.sample_id == query.c.sample_id, isouter=True)

        if require_has_publication:
            # Return a sample only if it has a publication number assigned to it
            mque = mque.filter(func.json_array_length(pub_q.c.publications) > 0)

        storage_metadata_dict = storage_statistics()

        results = []
        for row in session.execute(mque).all():
            result = {
                "name": row.name,
                "version": row.version,
                "request_id": row.request_id,
                "filetype": row.filetype,
                "state": row.state,
                "last_state_update": row.last_state_update,
                "transformations": row.transformations,
                "storage_use": storage_metadata_dict.get(
                    (
                        row.transformations[-1]["id"] if row.transformations else None,
                        row.filetype,
                    ),
                    0,
                ),
            }
            if row.progress is not None:
                result["progress"] = row.progress
            if row.jira_task is not None:
                result["jira_task"] = row.jira_task
            if row.merge_request is not None:
                result["merge_request"] = row.merge_request
            result.update(
                {
                    "wg": row.wg,
                    "analysis": row.analysis,
                    "sample_id": row.sample_id,
                    # TODO: Remove
                    "owners": [],
                    "validity_start": row.validity_start,
                    "validity_end": row.validity_end,
                    "housekeeping_interaction_due": row.housekeeping_interaction_due,
                    "publications": row.publications or [],
                }
            )
            results.append(result)
        return results

    @inject_session
    def getArchivedRequests(self, *, state=None, session: Session):
        sq = (
            session.query(AP.request_id, AP.filetype)
            .filter(or_(AP.validity_end.is_(None), datetime.datetime.now() < AP.validity_end))
            .distinct()
            .subquery()
        )
        query = session.query(Request).filter(~tuple_(Request.request_id, Request.filetype).in_(select(sq)))
        if state is not None:
            query = query.filter(AP.state == state)
        return [result.toDict() for result in query]

    @inject_session
    def getTags(self, wg, analysis, *, at_time=None, session: Session):
        return _getTags(session, wg=wg, analysis=analysis, at_time=at_time)

    @inject_session
    def getKnownAutoTags(self, *, session) -> set:
        return _getKnownAutoTags(session)

    @inject_session
    def registerTransformations(self, transforms: dict[int, dict[str, list[dict]]], *, session: Session):
        if not transforms:
            raise ValueError("No transforms passed")
        transforms = deepcopy({(prid, ft): ts for prid, x in transforms.items() for ft, ts in x.items()})
        for request in session.query(Request).filter(tuple_(Request.request_id, Request.filetype).in_(transforms)):
            knownTransforms = {t["id"] for t in request.extra_info["transformations"]}
            for transform in transforms.pop((request.request_id, request.filetype)):
                if transform["id"] in knownTransforms:
                    raise ValueError(f"Transformation is already known {transform['id']}")
                # TODO: Validate the transform object
                request.extra_info["transformations"].append(transform)
                # By default SQLAlchemy doesn't detect changes in JSON columns when using the ORM
                # Ideally this should be fixed in the database definition but flagging manually is
                # good enough for now
                flag_modified(request, "extra_info")
        if transforms:
            raise ValueError(f"Did not find requests for IDs: {list(transforms)}")

    @inject_session
    def deregisterTransformations(self, tIDs: dict[int, dict[str, list[int]]], *, session: Session):
        """See :meth:`~.AnalysisProductionsClient.registerTransformations`"""
        if not tIDs:
            raise ValueError("No transform IDs passed")
        tIDs = deepcopy({(prid, ft): ts for prid, x in tIDs.items() for ft, ts in x.items()})
        query = session.query(Request).filter(tuple_(Request.request_id, Request.filetype).in_(tIDs))
        for request in query:
            for tID in tIDs.pop((request.request_id, request.filetype)):
                for i, transform in enumerate(request.extra_info["transformations"]):
                    if transform["id"] == tID:
                        request.extra_info["transformations"].pop(i)
                        break
                else:
                    raise ValueError(f"Transformation {tID} is not known")
                flag_modified(request, "extra_info")
        if tIDs:
            raise ValueError(f"Did not find requests for IDs: {list(tIDs)}")

    def registerRequests(self, requests: list[dict]):
        request_ids = {(r["request_id"], r["filetype"]) for r in requests}
        with self.session as session:
            known_ids = {
                (i, ft)
                for i, ft in session.query(AP.request_id, AP.filetype).filter(
                    tuple_(AP.request_id, AP.filetype).in_(request_ids)
                )
            }
            if known_ids:
                raise ValueError(f"Already registered requests: {known_ids!r}")

            for r in requests:
                self.log.info(
                    "Registering Analysis Production request",
                    f"{r['wg']} {r['analysis']} {r['version']} {r['request_id']} {r['name']}",
                )
                sample = AP(
                    request_id=r["request_id"],
                    filetype=r["filetype"],
                    name=r["name"],
                    version=r["version"],
                    wg=r["wg"],
                    analysis=r["analysis"],
                    validity_start=r["validity_start"],
                    extra_info=r["extra_info"],
                    auto_tags=[AutoTag(name=x["name"], value=x["value"]) for x in r["auto_tags"]],
                )
                session.add(sample)

        with self.session as session:
            query = session.query(AP)
            query = query.filter(tuple_(AP.request_id, AP.filetype).in_(request_ids))
            return [result.toDict() for result in query]

    @inject_session
    def addRequestsToAnalysis(self, wg: str, analysis: str, requests: list[tuple[int, str]], *, session: Session):
        self.log.info("Adding samples to analysis", f"({wg}/{analysis}) {','.join(map(str, requests))}")

        query = select(AP.request_id, AP.filetype, AP.sample_id).filter(
            AP.wg == wg,
            AP.analysis == analysis,
            tuple_(AP.request_id, AP.filetype).in_(requests),
            AP.validity_end.is_(None),
        )
        if already_existing := session.execute(query).all():
            raise ValueError(
                f"Some requests are already registered for {wg}/{analysis} request_id->sample_id mapping is "
                f"{ {(request_id, filetype): sample_id for request_id, filetype, sample_id in already_existing} }"
            )

        query = insert(AP).values(
            [
                {"wg": wg.lower(), "analysis": analysis.lower(), "request_id": request_id, "filetype": ft}
                for request_id, ft in requests
            ]
        )
        session.execute(query)

    @inject_session
    def archiveSamples(self, sample_ids: list[int], *, session: Session):
        self.log.info("Archiving Analysis Productions", ",".join(map(str, sample_ids)))
        query = session.query(AP.sample_id)
        query = query.filter(AP.sample_id.in_(sample_ids))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Unknown sample IDs passed {known_sample_ids - set(sample_ids)!r}")
        query = query.filter(AP.validity_end.is_(None))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Some samples have already been archived {known_sample_ids - set(sample_ids)!r}")
        query = session.query(AP).filter(AP.sample_id.in_(sample_ids))
        query.update({"validity_end": func.now()})  # pylint: disable=not-callable

    @inject_session
    def archiveSamplesAtSpecificTime(self, sample_ids: list[int], archive_time: datetime.datetime, *, session: Session):
        self.log.info(f"Archiving Analysis Productions at {archive_time}", ",".join(map(str, sample_ids)))
        query = session.query(AP.sample_id)
        query = query.filter(AP.sample_id.in_(sample_ids))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Unknown sample IDs passed {known_sample_ids - set(sample_ids)!r}")
        query = query.filter(AP.validity_end.is_(None))
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Some samples have already been archived {known_sample_ids - set(sample_ids)!r}")
        query = session.query(AP).filter(AP.sample_id.in_(sample_ids))

        query.update({"validity_end": archive_time})  # pylint: disable=not-callable

    @inject_session
    def delayHousekeepingInteractionDue(
        self, sample_ids: list[int], next_interaction_due: datetime.datetime, *, session: Session
    ):
        self.log.info(
            "Delaying next Analysis Productions housekeeping interaction",
            f"to {next_interaction_due} for Analysis Production IDs {','.join(map(str, sample_ids))}",
        )
        query = session.query(AP.sample_id)
        query = query.filter(AP.sample_id.in_(sample_ids))

        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Unknown sample IDs passed {known_sample_ids - set(sample_ids)!r}")
        query = query.filter(AP.validity_end.is_(None))  # don't bother with archived samples
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(sample_ids):
            raise ValueError(f"Some samples have already been archived {known_sample_ids - set(sample_ids)!r}")
        query = session.query(AP).filter(AP.sample_id.in_(sample_ids))

        query.update({"housekeeping_interaction_due": next_interaction_due})  # pylint: disable=not-callable

    @inject_session
    def getHousekeepingInteractionDueNow(self, *, session: Session):
        query = select(
            AP.wg,
            AP.analysis,
            case(
                (
                    func.sum(AP.housekeeping_interaction_due.is_not(None)) == 0,  # pylint: disable=not-callable
                    func.json_object(type_=JSON),  # pylint: disable=not-callable
                ),
                else_=json_group_object(AP.sample_id, AP.housekeeping_interaction_due),
            ).label("samples_due"),
        )
        # confirm it is not archived
        query = query.filter(AP.validity_end.is_(None))
        # confirm due date is in the past
        query = query.filter(AP.housekeeping_interaction_due <= func.now())  # pylint: disable=not-callable
        query = query.group_by(AP.wg, AP.analysis)
        query = query.subquery(name="samples")

        owner = select(
            AnalysisOwner.wg,
            AnalysisOwner.analysis,
            json_group_array(AnalysisOwner.username).label("owner_usernames"),
        )
        # Only get current owners (those with active validity periods)
        current_time = func.now()  # pylint: disable=not-callable
        owner = owner.where(
            and_(
                AnalysisOwner.validity_start <= current_time,
                or_(AnalysisOwner.validity_end.is_(None), AnalysisOwner.validity_end > current_time),
            )
        )
        owner = owner.group_by(AnalysisOwner.wg, AnalysisOwner.analysis)
        owner = owner.subquery(name="owners")

        fq = select(query, owner.c.owner_usernames)
        fq = fq.join(owner, and_(query.c.wg == owner.c.wg, query.c.analysis == query.c.analysis), isouter=True)
        samples_due = [dict(row._mapping) for row in session.execute(fq).all()]
        return samples_due

    @inject_session
    def addPublication(self, sample_ids: list[int], publication_number: str, *, session: Session):
        if len(publication_number) > 64:
            raise ValueError("This publication number is too long (>64 chars)")

        query = insert(Publication).values([{"number": publication_number, "sample_id": sid} for sid in sample_ids])
        session.execute(query)

    @inject_session
    def getPublications(self, sample_ids: list[int] | None = None, *, session: Session):
        numbers = defaultdict(list)

        ap_q = select(
            AP.wg,
            AP.analysis,
            AP.sample_id,
            AP.validity_start,
            AP.validity_end,
            AP.name,
            AP.version,
            AP.request_id,
            AP.filetype,
            AP.state,
        ).subquery(name="samples")

        query = select(Publication.number, Publication.sample_id, ap_q)
        query = query.join(ap_q, ap_q.c.sample_id == Publication.sample_id)

        if sample_ids:
            query = query.filter(Publication.sample_id.in_(sample_ids))
        for row in session.execute(query).all():
            numbers[row.number].append(
                {
                    "sample_id": row.sample_id,
                    "request_id": row.request_id,
                    "filetype": row.filetype,
                    "wg": row.wg,
                    "analysis": row.analysis,
                    "name": row.name,
                    "version": row.version,
                    "state": row.state,
                    "validity_start": row.validity_start,
                    "validity_end": row.validity_end,
                }
            )
        return numbers

    @inject_session
    def setState(self, newState: dict[tuple[int, str], dict], *, session: Session):
        for request_id_ft, updateDict in newState.items():
            query = session.query(Request).filter(tuple_(Request.request_id, Request.filetype) == request_id_ft)
            rowsUpdated = query.update({getattr(Request, k): v for k, v in updateDict.items()})
            if rowsUpdated != 1:
                raise ValueError(
                    f"Failed to update Request({request_id_ft}) with {updateDict!r}, {rowsUpdated} matching rows found"
                )

    @inject_session
    def commitBulkDatasetActions(self, wg: str, analysis: str, body: ActionsInputModel, *, session: Session):
        """
        Commit bulk dataset actions (archive, extend housekeeping, add publications).

        This is an atomic operation - either all changes succeed or all fail.
        Returns detailed information about the operations performed.
        """
        # Collect all operations to perform
        updates = defaultdict(dict)
        publication_inserts = []
        action_summary = defaultdict(int)  # Count actions by type
        action_map = {}  # Maps sample_id to action type for duplicate detection

        def modify_sample(
            sample_id: int,
            action_type: str,
            validity_end: datetime.datetime | None = None,
            add_publications: list[str] | None = None,
            housekeeping_interaction_due: datetime.datetime | None = None,
        ):
            # Check for duplicate sample_id across different action types
            if sample_id in action_map:
                raise ValueError(
                    f"Sample ID {sample_id} already has the action '{action_map[sample_id]}', "
                    f"cannot also apply action '{action_type}'"
                )
            update_dict = {"sample_id": sample_id}
            if validity_end is not None:
                update_dict["validity_end"] = validity_end
            if add_publications is not None:
                publication_inserts.extend(
                    {"number": pub_number, "sample_id": sample_id} for pub_number in add_publications
                )
            if housekeeping_interaction_due is not None:
                update_dict["housekeeping_interaction_due"] = housekeeping_interaction_due
            updates[sample_id].update(update_dict)
            action_map[sample_id] = action_type
            action_summary[action_type] += 1

        # Process deletes
        if body.delete:
            for delete in body.delete:
                modify_sample(
                    sample_id=delete.sample_id,
                    action_type="delete",
                    validity_end=func.now(),  # pylint: disable=not-callable
                    add_publications=delete.add_publications,
                )

        # Calculate new housekeeping dates
        now = datetime.datetime.now(datetime.UTC)

        # Process one_month extensions
        if body.one_month:
            one_month_later = now + datetime.timedelta(days=30)
            for sample in body.one_month:
                modify_sample(
                    sample_id=sample.sample_id,
                    action_type="extend_one_month",
                    housekeeping_interaction_due=one_month_later,
                    add_publications=sample.add_publications,
                )

        # Process three_months extensions
        if body.three_months:
            three_months_later = now + datetime.timedelta(days=90)
            for sample in body.three_months:
                modify_sample(
                    sample_id=sample.sample_id,
                    action_type="extend_three_months",
                    housekeeping_interaction_due=three_months_later,
                    add_publications=sample.add_publications,
                )

        # Process six_months extensions
        if body.six_months:
            six_months_later = now + datetime.timedelta(days=183)
            for sample in body.six_months:
                modify_sample(
                    sample_id=sample.sample_id,
                    action_type="extend_six_months",
                    housekeeping_interaction_due=six_months_later,
                    add_publications=sample.add_publications,
                )

        # Early return if no changes
        if not updates and not publication_inserts:
            return {
                "status": "success",
                "message": "No changes to apply",
                "samples_updated": 0,
                "publications_added": 0,
                "actions": {},
            }

        # Validate all sample IDs exist and belong to this analysis BEFORE any changes
        all_sample_ids = list(updates.keys())
        query = session.query(AP.sample_id).filter(
            AP.sample_id.in_(all_sample_ids),
            AP.wg == wg.lower(),
            AP.analysis == analysis.lower(),
        )
        query = _filterForTime(query, AP, at_time=None)
        known_sample_ids = {i for i, in query}
        if len(known_sample_ids) != len(all_sample_ids):
            unknown_ids = set(all_sample_ids) - known_sample_ids
            raise ValueError(f"Unknown or unauthorized sample IDs: {sorted(unknown_ids)}")

        # Validate publication numbers BEFORE any changes
        if publication_inserts:
            for pub in publication_inserts:
                if len(pub["number"]) > 64:
                    raise ValueError(f"Publication number too long (>64 chars): {pub['number']}")

        # All validation passed - now perform the transaction atomically
        with session.begin_nested():
            # Apply updates to samples
            for sample_id, update_dict in updates.items():
                # Remove sample_id from update_dict before updating
                update_values = {k: v for k, v in update_dict.items() if k != "sample_id"}
                if update_values:
                    query = session.query(AP).filter(AP.sample_id == sample_id)
                    rows_updated = query.update(update_values)
                    if rows_updated == 0:
                        raise ValueError(f"Sample {sample_id} not found or already processed")

            # Insert publications
            if publication_inserts:
                query = insert(Publication).values(publication_inserts)
                session.execute(query)

        # Return success with summary
        return {
            "status": "success",
            "message": f"Successfully processed {len(updates)} sample(s)",
            "samples_updated": len(updates),
            "publications_added": len(publication_inserts),
            "actions": dict(action_summary),
        }

    @inject_session
    def setTags(self, oldTags: dict[int, dict[str, str]], newTags: dict[int, dict[str, str]], *, session: Session):
        if set(oldTags) != set(newTags):
            raise ValueError("oldTags and newTags must contain the same keys")
        # Tags should always be lowercase in the database
        oldTags = {int(i): {str(k).lower(): str(v).lower() for k, v in x.items()} for i, x in oldTags.items()}
        newLengths = {int(i): len(x) for i, x in newTags.items()}
        newTags = {int(i): {str(k).lower(): str(v).lower() for k, v in x.items()} for i, x in newTags.items()}
        if newLengths != {i: len(x) for i, x in newTags.items()}:
            raise ValueError("newTags contains duplicate keys when converted to lowercase")

        # Compute what needs to be changed, while also ensuring the auto tags aren't touched
        knownAutoTags = _getKnownAutoTags(session)
        toRemove = []
        toAdd = []
        for sample_id, old in oldTags.items():
            new = newTags[sample_id]
            removed_tags = set(old) - set(new)
            modified_tags = {k: new[k] for k in set(new) & set(old) if new[k] != old[k]}
            added_tags = {k: new[k] for k in set(new) - set(old)}
            # Ensure that the automatic tags aren't being modifed
            if modifiedAutoTags := {*removed_tags, *modified_tags, *added_tags} & knownAutoTags:
                raise ValueError(f"Cannot modify AutoTags {modifiedAutoTags}")
            # Tags are modified by being removed and re-added allow for time-travel
            toRemove += [(sample_id, k) for k in {*removed_tags, *modified_tags}]
            toAdd += [(sample_id, k, v) for k, v in {**added_tags, **modified_tags}.items()]

        latestOldTags = _getTags(session, sample_ids=oldTags)
        if oldTags != latestOldTags:
            raise ValueError("oldTags is out of date")

        # Remove the old tags
        query = _filterForTime(session.query(Tag), Tag, at_time=None)
        query = query.filter(tuple_(Tag.sample_id, Tag.name).in_(toRemove))
        query.update({"validity_end": func.now()})  # pylint: disable=not-callable
        # Add the new tag values
        for sample_id, name, value in toAdd:
            session.add(Tag(sample_id=sample_id, name=name, value=value))

    @inject_session
    def getIdsMapping(self, *, session: Session):
        query = select(
            AP.wg,
            AP.analysis,
            AP.request_id,
            AP.filetype,
            AP.name,
            AP.version,
            func.JSON_EXTRACT(AP.extra_info, "$.transformations[*].id").label("transformation_ids"),
        )
        query.join(Request, tuple_(AP.request_id, AP.filetype) == tuple_(Request.request_id, Request.filetype))
        query = query.filter(AP.validity_end.is_(None))
        return list(dict(row._mapping) for row in session.execute(query).all())


def _getKnownAutoTags(session: Session):
    return {name for name, in session.query(AutoTag.name).distinct()}


def _getTags(session, *, wg=None, analysis=None, at_time=None, sample_ids=None):
    results = defaultdict(dict)

    # Get the automatic tags
    auto_query = select(AP.sample_id, AutoTag.name, AutoTag.value)
    auto_query = auto_query.join(AutoTag, and_(AP.request_id == AutoTag.request_id, AP.filetype == AutoTag.filetype))
    if sample_ids:
        auto_query = auto_query.filter(AP.sample_id.in_(sample_ids))
    auto_query = auto_query.filter(*_buildCondition(wg, analysis))
    auto_query = _filterForTime(auto_query, AP, at_time)

    # Get the manual tags
    manual_query = select(AP.sample_id, Tag.name, Tag.value)
    manual_query = manual_query.join(Tag, AP.sample_id == Tag.sample_id)
    if sample_ids:
        manual_query = manual_query.filter(AP.sample_id.in_(sample_ids))
    if wg is not None:
        manual_query = manual_query.filter(*_buildCondition(wg, analysis))
    manual_query = _filterForTime(manual_query, AP, at_time)
    manual_query = _filterForTime(manual_query, Tag, at_time)

    # Combine both queries using UNION ALL for better performance
    combined_query = auto_query.union_all(manual_query)

    for sample_id, name, value in session.execute(combined_query):
        results[sample_id][name] = value
    return dict(results)


def _filterForTime(query, obj, at_time):
    if at_time is None:
        at_time = func.now()  # pylint: disable=not-callable
    return query.filter(
        obj.validity_start <= at_time,
        or_(obj.validity_end.is_(None), at_time < obj.validity_end),
    )


def _buildCondition(wg, analysis=None, name=None, version=None):
    """Build a SQLAlchemy query for the AnalysisProductions table"""
    # Pre-lower the input values to avoid repeated function calls in SQL
    # Rely on the collation being case insensitive for comparisons
    if wg is not None:
        yield AP.wg == wg.lower()
    if analysis is not None:
        yield AP.analysis == analysis.lower()
    if name is not None:
        yield AP.name == name.lower()
    if version is not None:
        yield AP.version == version
