###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
.. versionadded:: v11.0.53

This agent consolidates data from the bookkeeping and the DFC, generates json out of it,
uploads them to a storage.
It also sends the accounting data to OpenSearch, and fill in 2 tables in the StorageUsageDB

.. literalinclude:: ../ConfigTemplate.cfg
  :start-after: ##BEGIN UserStorageDumpAgent
  :end-before: ##END UserStorageDumpAgent
  :dedent: 2
  :caption: UserStorageDumpAgent options

"""
# # imports
import asyncio
import json
import re
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from functools import lru_cache, partial
from pathlib import Path
from textwrap import dedent
from urllib.parse import quote_plus

from opensearchpy import OpenSearch, helpers


import numpy as np
import pandas as pd
import time


# # from DIRAC
from DIRAC import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise
from DIRAC.ConfigurationSystem.Client.Utilities import getDBParameters
from DIRAC.DataManagementSystem.DB.FileCatalogDB import FileCatalogDB
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDumpDB import StorageUsageDumpDB


# Before 90 days, we keep all the dumps
# After 90 days, we keep the first per day
# After a year, we keep the first per week
OS_DAILY_RETENTION = 90
OS_WEEKLY_RETENTION = 365

# We keep all the weekly dumps
# We keep the daily dump for a year
S3_DAILY_RETENTION = 365

AGENT_NAME = "DataManagement/UserStorageDumpAgent"

USER_ROOT_DIR = "/lhcb/user"

S3_BUCKET_NAME = "lhcbdirac"
S3_ENDPOINT_URL = "https://s3.cern.ch:443"
OS_ENDPOINT_URL = "os-lhcb-dirac.cern.ch:443/os"
OS_INDEX_PREFIX = "lhcb_storage_user_usage_index_"


async def returnValueOrRaiseAsync(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return returnValueOrRaise(await loop.run_in_executor(None, func, *args, **kwargs))


def sendToOpenSearch(df: pd.DataFrame, hosts: str, http_auth: tuple[str, str]):
    """
    Sends the data to OpenSearch
    """
    log = gLogger.getSubLogger("sendToOpenSearch")
    log.info("Sending to OpenSearch")
    start_time = time.time()

    fields = {
        "SEName": {"type": "keyword"},
        "User": {"type": "keyword"},
        "UserStatus": {"type": "keyword"},
        "SESize": {"type": "long"},
        "SEFiles": {"type": "long"},
        "timestamp": {"type": "date"},
    }

    # Create an OpenSearch client
    client = OpenSearch(
        hosts=hosts,
        http_auth=http_auth,
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )

    template_body = {
        "template": {"mappings": {"properties": fields}},
        "index_patterns": [f"{OS_INDEX_PREFIX}*"],
        "priority": 5,
    }
    result = client.indices.put_index_template(name=OS_INDEX_PREFIX, body=template_body)
    assert result["acknowledged"]

    utc_now = datetime.now(tz=timezone.utc)
    timestamp = utc_now.strftime("%Y-%m-%dT%H:%M")
    as_date = utc_now.isocalendar()
    index_timestamp = f"{as_date[0]}-{as_date[1]}"

    data = df.reset_index(drop=True).to_dict("records")

    actual_index = f"{OS_INDEX_PREFIX}{index_timestamp}"
    for entry in data:
        # entry.pop("Unnamed: 0")

        entry["_index"] = actual_index
        entry["_id"] = f"{entry['SEName']}_{entry['User']}_{timestamp}"
        entry["timestamp"] = utc_now

    succeeded = []
    failed = []
    for success, item in helpers.parallel_bulk(
        client,
        actions=data,
        chunk_size=500,
        raise_on_error=False,
        raise_on_exception=False,
        max_chunk_bytes=20 * 1024 * 1024,
        request_timeout=60,
    ):

        if success:
            succeeded.append(item)
        else:
            failed.append(item)

    if len(failed) > 0:
        log.error("There were errors: ", f"{len(failed)}")
        for item in failed:
            log.error(f"    {item}")

    if len(succeeded) > 0:
        log.info("Bulk-inserted", f"{len(succeeded)} items.")
    log.info("Upload duration", f"{time.time() - start_time:.2f} secs")
    return S_OK()


async def get_users_usage():
    db = FileCatalogDB()
    columns = ["Name", "SEName", "SESize", "SEFiles"]
    parent_id = await returnValueOrRaiseAsync(
        db._query,
        f"SELECT DirID from FC_DirectoryList where Name = '{USER_ROOT_DIR}'",
    )

    query = """
    with parent_id as (select ChildID from FC_DirectoryClosure where ParentID = %s and Depth = 2)
    SELECT d.Name, SEName, SUM(du.SESize), SUM(du.SEFiles)
    FROM FC_DirectoryUsage du
    JOIN FC_DirectoryClosure dc ON du.DirID = dc.ChildID
    JOIN parent_id p ON dc.ParentID = p.ChildID
    JOIN FC_DirectoryList d on d.DirID = p.ChildID
    JOIN FC_StorageElements se on se.SEID = du.SEID
    group by p.ChildID, du.SEID;
    """

    # We can't work with db._query because we change the isolation level
    conn = returnValueOrRaise(db._getConnection())

    with conn.cursor() as cursor:
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")

        cursor.execute("SELECT @@transaction_isolation;")

        query = dedent(query.strip())
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, cursor.execute, query, parent_id)
        return columns, await loop.run_in_executor(None, cursor.fetchall)


def get_user_status(username: str, users_status: dict[str:bool]):
    if username not in users_status:
        return "Missing"
    if users_status[username]:
        return "Suspended"
    return "OK"


class UserStorageDumpAgent(AgentModule):

    def initialize(self):
        self.workDirectory = self.am_getWorkDirectory()
        self.os_endpoint_url = self.am_getOption("OS_endpoint_url", OS_ENDPOINT_URL)
        self.os_username = gConfig.getValue("/Systems/NoSQLDatabases/User")
        self.os_password = gConfig.getValue("/Systems/NoSQLDatabases/Password")

        self.storageUsageDumpDB = StorageUsageDumpDB()

        return S_OK()

    def execute(self):
        asyncio.run(self.do_the_dump())
        return S_OK()

    async def do_the_dump(self):

        user_storage = await get_users_usage()
        dfc_df = pd.DataFrame(user_storage[1], columns=user_storage[0])
        dfc_df["User"] = dfc_df.Name.apply(lambda x: x.split("/")[-1])

        users_status = {
            user: ("lhcb" in gConfig.getOptionsDict(f"/Registry/Users/{user}")["Value"].get("Suspended", ""))
            for user in gConfig.getSections("/Registry/Users")["Value"]
        }
        _get_user_status = partial(get_user_status, users_status=users_status)
        dfc_df["UserStatus"] = dfc_df.User.apply(_get_user_status)
        dfc_df.drop("Name", axis=1, inplace=True)

        # Only keep the rows for which there are size and files
        dfc_df = dfc_df[(dfc_df.SESize != 0) & (dfc_df.SEFiles != 0)]

        dfc_df.to_csv("/tmp/user_storage.csv.zst", index=False)

        await asyncio.gather(
            returnValueOrRaiseAsync(
                partial(sendToOpenSearch, dfc_df, self.os_endpoint_url, (self.os_username, self.os_password))
            ),
            returnValueOrRaiseAsync(user_storage_to_sql, dfc_df, self.storageUsageDumpDB),
            # returnValueOrRaiseAsync(
            #     partial(
            #         storage_summary_to_sql,
            #         df,
            #         self.storageUsageDumpDB,
            #     )
            # ),
        )


def user_storage_to_sql(df, db: StorageUsageDumpDB):
    log = gLogger.getLocalSubLogger("user_storage_to_sql")
    log.info("Writing user directory metadata to database")
    start_time = time.time()
    db.user_storage_to_sql(df)
    log.info("Upload duration", f"{time.time() - start_time:.2f} secs")
    return S_OK()
