#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""This module contains the AccountApiClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ROLE_API_VERSION = 1


class RoleApiClientOnPrem(BaseAPIClient):
    """The API client of the Role."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = None,
    ) -> None:
        """Initializes the RoleApiClientOnPrem.

        Args:
            auth: The Authentication object.
            base_url: The Role Service URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"usermgmt/v{DEFAULT_ROLE_API_VERSION}"

    def get_roles(
        self,
        params: dict | None = None,
    ) -> requests.Response:
        """Get account owner details for a given account ID.

        Args:
            params: Params to filter by. This can contain: account_id, service_name, source_service_name, policy_type,
                    service_group_id.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/roles"
        return self.get(url=url, params=params)

    def create_role(self, data: str) -> requests.Response:
        """Creates a custom role for a specific service within the account.

        Args:
            data: Data to create a role. this should contain: name, display_name, description, account_id,
                  service_name, actions.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/role"
        response = self.post(url=url, data=data)
        return response

    def update_role(self, role_id: str, data: str) -> requests.Response:
        """Updates a custom role.

        Args:
            role_id: The role id.
            data: Data to update a role. Possible fields are: display_name, description, actions.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/role/{role_id}"
        response = self.put(url=url, data=data)
        return response

    def delete_role(self, role_id: str) -> requests.Response:
        """Delete a role by providing a role ID.

        Args:
            role_id: The role id.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/role/{role_id}"
        response = self.delete(url=url)
        return response
