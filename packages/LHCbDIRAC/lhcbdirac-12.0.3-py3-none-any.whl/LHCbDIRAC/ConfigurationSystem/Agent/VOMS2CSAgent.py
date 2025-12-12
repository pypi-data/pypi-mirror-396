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
from DIRAC import S_OK
from DIRAC.ConfigurationSystem.Client.CSAPI import CSAPI
from DIRAC.ConfigurationSystem.Client.Helpers import getVO
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getUsersInVO
from DIRAC.ConfigurationSystem.Agent.VOMS2CSAgent import VOMS2CSAgent as VOMS2CSAgentBase
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise

from LHCbDIRAC.ConfigurationSystem.Utilities.FenceIntegration import FenceIntegration


class VOMS2CSAgent(VOMS2CSAgentBase):
    """
    Extended VOMS2CSAgent to synchronise information with LBFence.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.csapi = CSAPI()
        self.lbfence = FenceIntegration()

    def initialize(self):
        """
        Extended initialize method.
        """
        init = super().initialize()
        if not init["OK"]:
            return init

        return init

    def execute(self):
        """
        Extended execute method to include Fence synchronization.
        """
        exec_res = super().execute()
        if not exec_res["OK"]:
            return exec_res

        vo = getVO("lhcb")

        ccid_to_end_date = {
            # We fall back to CCID if personId is not available
            # and have fallbacks for endDateInLHCbString because it's not clear how fence decides to return things...
            # however they are equivalent
            int(member.get("personId", member.get("CCID"))): member.get(
                "endDateInLHCbString", member.get("END_DATE_IN_LHCB_STRING")
            )
            for member in self.lbfence.get_all_memberships()
        }

        # Get all users from CS and update their AffiliationEnds for lhcb VO

        returnValueOrRaise(self.csapi.downloadCSData())
        users = returnValueOrRaise(self.csapi.describeUsers(getUsersInVO(vo)))

        for nick, user in users.items():
            if not (person_id := user.get("CERNPersonId", None)):
                continue  # No Person ID, cannot map
            if end_date := ccid_to_end_date.get(int(person_id), None):
                self.csapi.modifyUser(nick, {"AffiliationEnds": {**user.get("AffiliationEnds", {}), vo: end_date}})

        # Commit changes to CS
        returnValueOrRaise(self.csapi.commitChanges())

        return S_OK()
