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
"""Table/object defintions used in the AnalysisProductionsDB"""
import re
from sqlalchemy import (
    Boolean,
    ForeignKeyConstraint,
    Integer,
    Column,
    String,
    JSON,
    DateTime,
    func,
    ForeignKey,
    Float,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import TypeEngine
from pydantic import BaseModel, field_validator, ValidationError

Base = declarative_base()
Base.__table_args__ = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8",
}


class utcnow_add_days(expression.FunctionElement):
    """Sqlalchemy function to return a date now() plus 'days_to_add' days.

    Used to set default datetime as NOW() plus some number of days.

    """

    type: TypeEngine = DateTime()
    inherit_cache: bool = True

    def __init__(self, *args, days_to_add, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not isinstance(days_to_add, int):
            raise TypeError(f"days_to_add must be an int, got {type(days_to_add)}")
        self._days_to_add = days_to_add


@compiles(utcnow_add_days, "mysql")
def mysql_utcnow_add_days(element, compiler, **kw) -> str:
    """Sqlalchemy function for mysql rendering of utcnow_add_days.

    Part of utcnow_add_days.
    """
    return f"DATE_ADD( UTC_TIMESTAMP, INTERVAL {element._days_to_add} DAY)"


@compiles(utcnow_add_days, "sqlite")
def sqlite_utcnow_add_days(element, compiler, **kw) -> str:
    """Sqlalchemy function for sqlite rendering of utcnow_add_days.

    Part of utcnow_add_days.
    """
    return f"DATE(DATETIME('now'), '+{element._days_to_add} days')"


class Request(Base):
    __tablename__ = "ap_requests"

    VALID_STATES = [
        "waiting",
        "active",
        "replicating",
        "ready",
    ]
    request_id = Column(Integer, primary_key=True)
    filetype = Column(String(64), primary_key=True)
    state = Column(String(16), nullable=False, default="waiting")
    progress = Column(Float, nullable=True)
    last_state_update = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    )

    name = Column(String(256), nullable=False)
    version = Column(String(64), nullable=False)
    auto_tags = relationship("AutoTag", back_populates="request", lazy="selectin")
    # TODO: Use the mutable extension and validate this object better?
    extra_info = Column(JSON(), nullable=False, default=lambda: {"transformations": []})

    @validates("name")
    def convert_lower(self, key, value):
        return value.lower()

    def toDict(self):
        result = {
            "name": self.name,
            "version": self.version,
            "request_id": self.request_id,
            "filetype": self.filetype,
            "state": self.state,
            "last_state_update": self.last_state_update,
            "transformations": self.extra_info["transformations"],
        }
        if self.progress is not None:
            result["progress"] = self.progress
        if "jira_task" in self.extra_info:
            result["jira_task"] = self.extra_info["jira_task"]
        if "merge_request" in self.extra_info:
            result["merge_request"] = self.extra_info["merge_request"]
        return result


class AnalysisSample(Request):
    __tablename__ = "ap_analysis_samples"

    sample_id = Column(Integer, primary_key=True)
    wg = Column(String(16), nullable=False)
    analysis = Column(String(256), nullable=False)
    request_id = Column(Integer, nullable=False)
    filetype = Column(String(64), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(["request_id", "filetype"], ["ap_requests.request_id", "ap_requests.filetype"]),
    )

    tags = relationship("Tag", back_populates="sample", lazy="selectin")
    publications = relationship("Publication", back_populates="sample", lazy="selectin")

    # Allow this table to be temporally versioned
    validity_start = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()  # pylint: disable=not-callable
    )
    validity_end = Column(DateTime(timezone=False), nullable=True)

    housekeeping_interaction_due = Column(DateTime(timezone=False), server_default=utcnow_add_days(days_to_add=90))

    @validates("wg", "analysis")
    def convert_lower(self, key, value):
        return value.lower()

    def toDict(self):
        result = Request.toDict(self)
        result.update(
            {
                "wg": self.wg,
                "analysis": self.analysis,
                "sample_id": self.sample_id,
                "owners": [],
                "validity_start": self.validity_start,
                "validity_end": self.validity_end,
                "housekeeping_interaction_due": self.housekeeping_interaction_due,
                "publications": self.publications or [],
            }
        )
        return result


class User(Base):
    __tablename__ = "ap_users"

    username = Column(String(256), nullable=False, primary_key=True)
    active_since = Column(DateTime(timezone=False), nullable=False, default=func.now())  # pylint: disable=not-callable
    active_until = Column(DateTime(timezone=False), nullable=True)

    n_requests = Column(Integer, nullable=False, default=0)
    accepted_agreement = Column(DateTime(timezone=False), nullable=True, default=None)
    trusted = Column(Boolean, nullable=False, default=False)

    # Links the user to Fence as the username is not used there
    person_id = Column(Integer, nullable=True)

    @validates("username")
    def convert_lower(self, key, value):
        if value is None:
            return None
        return value.lower()

    def toDict(self):
        return {
            "username": self.username,
            "active_since": self.active_since,
            "active_until": self.active_until,
            "n_requests": self.n_requests,
            "accepted_agreement": self.accepted_agreement,
            "trusted": self.trusted,
            "person_id": self.person_id,
        }


class AnalysisOwner(Base):
    __tablename__ = "ap_analysis_owners"

    wg = Column(String(16), primary_key=True)
    analysis = Column(String(256), primary_key=True)
    username = Column(String(256), ForeignKey("ap_users.username"), primary_key=True)

    validity_start = Column(
        DateTime(timezone=False),
        nullable=False,
        primary_key=True,
        server_default=func.now(),  # pylint: disable=not-callable
    )
    validity_end = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()  # pylint: disable=not-callable
    )

    # Add relationship to User
    user = relationship("User", foreign_keys=[username])

    @validates("username", "wg", "analysis")
    def convert_lower(self, key, value):
        return value.lower()

    def toDict(self):
        return {
            "wg": self.wg,
            "analysis": self.analysis,
            "username": self.username,
            "validity_start": self.validity_start.isoformat() if self.validity_start else None,
            "validity_end": self.validity_end.isoformat() if self.validity_end else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Publication(Base):
    __tablename__ = "ap_publications"

    id = Column(Integer, primary_key=True)
    number = Column(String(64), nullable=False)
    sample_id = Column(Integer, ForeignKey("ap_analysis_samples.sample_id"), nullable=False)
    sample = relationship("AnalysisSample", back_populates="publications", lazy="selectin")

    __table_args__ = (UniqueConstraint("number", "sample_id", name="_pubnumber_sample_id_no_duplicates"),)

    @validates("number")
    def convert_upper(self, key, value):
        return value.upper()


class Tag(Base):
    __tablename__ = "ap_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    sample_id = Column(Integer, ForeignKey("ap_analysis_samples.sample_id"), nullable=False)
    sample = relationship("AnalysisSample", back_populates="tags", lazy="joined")

    # Allow this table to be temporally versioned
    validity_start = Column(
        DateTime(timezone=False), nullable=False, server_default=func.now()  # pylint: disable=not-callable
    )
    validity_end = Column(DateTime(timezone=False), nullable=True)

    @validates("name", "value")
    def convert_lower(self, key, value):
        return value.lower()


class AutoTag(Base):
    __tablename__ = "ap_auto_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    value = Column(String(64), nullable=False)
    # composite foreign keys
    request_id = Column(Integer, nullable=False)
    filetype = Column(String(64), nullable=False)
    request = relationship("Request", back_populates="auto_tags", lazy="joined", enable_typechecks=False)

    __table_args__ = (
        ForeignKeyConstraint(["request_id", "filetype"], ["ap_requests.request_id", "ap_requests.filetype"]),
    )

    @validates("name", "value")
    def convert_lower(self, key, value):
        return value.lower()


class ActionsInputModel(BaseModel):
    """
    Model for dataset actions input.
    """

    @staticmethod
    def validate_publication_number(pub_no: str) -> str:
        """
        Validate publication number format.

        Accepts:
        - LHCb publication format: LHCb-{TYPE}-YYYY-XXX where TYPE is PAPER, CONF, DP, THESIS, FIGURE, or ANA
        - DOI URL format: https://doi.org/... or http://dx.doi.org/...

        Args:
            pub_no: Publication number string to validate

        Returns:
            The validated publication number (stripped of whitespace)

        Raises:
            ValueError: If the publication number format is invalid
        """
        if not pub_no or not pub_no.strip():
            raise ValueError("Publication number cannot be empty")

        trimmed = pub_no.strip()

        # Check length
        if len(trimmed) > 64:
            raise ValueError(f"Publication number too long (>64 chars): {trimmed}")

        # DOI URL format: https://doi.org/... or http://dx.doi.org/...
        doi_url_pattern = re.compile(r"^https?://(dx\.)?doi\.org/.+$", re.IGNORECASE)
        if doi_url_pattern.match(trimmed):
            return trimmed

        # LHCb publication formats: LHCb-PAPER-YYYY-XXX, LHCb-CONF-YYYY-XXX, LHCb-DP-YYYY-XXX,
        # LHCb-THESIS-YYYY-XXX, LHCb-FIGURE-YYYY-XXX, LHCb-ANA-YYYY-XXX
        lhcb_pattern = re.compile(r"^LHCb-(PAPER|CONF|DP|THESIS|FIGURE|ANA)-\d{4}-\d{3}$", re.IGNORECASE)
        if lhcb_pattern.match(trimmed):
            return trimmed

        # Provide helpful error messages
        if trimmed.startswith("http"):
            raise ValueError("Only https://doi.org/ or http://dx.doi.org/ URLs are accepted")

        if not trimmed.startswith("LHCb-"):
            raise ValueError("Publication number must start with 'LHCb-' or be a DOI URL")

        if not re.search(r"LHCb-(PAPER|CONF|DP|THESIS|FIGURE|ANA)", trimmed, re.IGNORECASE):
            raise ValueError("Publication type must be PAPER, CONF, DP, THESIS, FIGURE, or ANA")

        if not re.search(r"\d{4}", trimmed):
            raise ValueError("Publication number must include 4-digit year")

        if not re.search(r"\d{3}$", trimmed):
            raise ValueError("Publication number must end with 3-digit number")

        raise ValueError(
            f"Invalid publication number format: {trimmed}. Expected format: LHCb-{{TYPE}}-YYYY-XXX or https://doi.org/..."
        )

    class ReferSample(BaseModel, extra="ignore"):
        sample_id: int
        add_publications: list[str] | None = None

        @field_validator("add_publications")
        @classmethod
        def validate_publications(cls, v):
            """Validate each publication number in the list"""
            if v is None:
                return v
            validated = []
            errors = []
            for pub_no in v:
                try:
                    validated.append(ActionsInputModel.validate_publication_number(pub_no))
                except ValueError as e:
                    errors.append(str(e))

            if errors:
                raise ValueError(f"Invalid publication numbers: {'; '.join(errors)}")

            return validated

    # archive
    delete: list[ReferSample] = []

    # reminder extensions
    one_month: list[ReferSample] = []
    three_months: list[ReferSample] = []
    six_months: list[ReferSample] = []
