###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

from threading import Lock
from cachetools import TTLCache, cached
from DIRAC.ConfigurationSystem.Client.CSAPI import CSAPI
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise


@cached(cache=TTLCache(1, 10 * 60), lock=Lock())
def cern_username_to_person_id_mapping():
    """Convert CERN username to CERN Person ID using the CS."""
    users = returnValueOrRaise(CSAPI().describeUsers())
    mapping = {}
    for _, attributes in users.items():
        if "PrimaryCERNAccount" not in attributes:
            continue
        if "CERNPersonId" not in attributes:
            continue
        if attributes.get("CERNAccountType") not in ["Primary", "Secondary"]:
            continue
        mapping[attributes["PrimaryCERNAccount"]] = attributes["CERNPersonId"]
    return mapping


def cern_username_to_person_id(username: str):
    """Convert CERN username to CERN Person ID using CS lookup."""
    try:
        return cern_username_to_person_id_mapping().get(username, None)
    except Exception:
        return None
