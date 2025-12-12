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
import logging
from threading import Lock
from urllib.parse import quote_plus

from cachetools import TTLCache, cached
import requests

from DIRAC import gConfig, gLogger

from LHCbDIRAC.ConfigurationSystem.Utilities.CERNSSOAPIToken import CERNSSOAPIToken


class FenceIntegration:
    """Class for talking to the LHCb Fence membership API."""

    def __init__(self, fence_url=None, token: CERNSSOAPIToken | None = None):
        """Initialize FenceIntegration.

        Args:
            fence_url: Fence API base URL. If None, will try to get from DIRAC config.
            token: CERNSSOAPIToken object. If None, will try to set-up from DIRAC config.
        """
        self.fence_url = fence_url or self._get_fence_url()
        self.token = token or self._get_token()
        self.log = gLogger.getSubLogger("FenceIntegration")

    def _get_fence_url(self):
        """Get Fence URL from DIRAC configuration."""
        return gConfig.getValue(
            "/Systems/Configuration/Agents/VOMS2CSAgent/FenceIntegration/URL", "https://lbfence.cern.ch"
        )

    def _get_token(self) -> CERNSSOAPIToken:
        """Get exchange-able token from DIRAC configuration."""
        audience = gConfig.getValue(
            "/Systems/Configuration/Agents/VOMS2CSAgent/FenceIntegration/Audience", "lhcb-membership-api-prod"
        )
        client_id = gConfig.getValue(
            "/Systems/Configuration/Agents/VOMS2CSAgent/FenceIntegration/ClientID", "lhcbdirac-fence-integration"
        )
        client_secret = gConfig.getValue("/Systems/Configuration/Agents/VOMS2CSAgent/FenceIntegration/ClientSecret", "")
        return CERNSSOAPIToken(audience=audience, client_id=client_id, client_secret=client_secret)

    def membership_search(self, query, *, offset: int = 0, limit: int = 1000):
        """Search for members in Fence.

        Args:
            query: Search query string
            offset: Result offset for pagination
            limit: Maximum number of results to return

        Returns:
            Tuple of (total_count, results_list)
        """
        data = {"results": []}
        try:
            result = requests.get(
                (
                    f"{self.fence_url}/membership/api/members/search"
                    f"?offset={offset}&limit={limit}&queryString={quote_plus(query)}"
                ),
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.token.token}",
                },
                verify=False,
                timeout=45,
            )
            result.raise_for_status()
            data = result.json()
        except Exception as e:
            self.log.error("Failed to query fence", str(e))
            raise

        return int(data.get("numberOfResults", 0)), data.get("results", [])

    def get_members(self, query_string):
        """Get all members matching a query string.

        Args:
            query_string: Fence query string to search for members

        Returns:
            List of member dictionaries
        """
        member_results = []
        n_processed = 0
        n_members = float("inf")  # Initialize to infinity so the loop runs at least once
        page = 0
        limit = 500
        self.log.info("Querying fence with:", query_string)
        while n_processed < n_members:
            self.log.info("Querying fence for members:", f"offset={page * limit}, limit={limit}")
            n_members, members = self.membership_search(query=query_string, offset=page * limit, limit=limit)
            member_results.extend(members)
            n_processed += len(members)
            page += 1
            self.log.info("Processed members from fence", f"{n_processed}/{n_members}")

        self.log.info("Finished querying members from fence", f"{n_processed} total")
        return member_results

    def get_all_memberships(self):
        """Query all fence memberships across all employment statuses.

        Returns:
            List of all member dictionaries
        """
        query_strings = [
            """( "employmentStatus" = "Inactive" )""",
            """( "employmentStatus" = "Active" )""",
            """( "employmentStatus" = "Extended" )""",
            """( "employmentStatus" = "Upcoming" )""",
        ]
        everyone_agg = []
        for query_string in query_strings:
            everyone_agg.extend(self.get_members(query_string=query_string))
        return everyone_agg
