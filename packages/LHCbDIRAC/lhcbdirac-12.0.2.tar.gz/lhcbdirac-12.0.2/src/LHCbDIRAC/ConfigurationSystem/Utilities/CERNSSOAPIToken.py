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
import requests


class CERNSSOAPIToken:
    def __init__(
        self,
        audience: str,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience

    @property
    def token(self):
        """Exchange for an api token for the given audience.
        See: https://auth.docs.cern.ch/user-documentation/oidc/api-access/
        """
        response = requests.post(
            "https://auth.cern.ch/auth/realms/cern/api-access/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "audience": self.audience,
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Could not get API token from {self.audience=}: {response.text}")

        return response.json().get("access_token")
