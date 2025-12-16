# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module containing the AccessGroupsApiClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ACCESS_GROUP_API_VERSION = 2


class AccessGroupsApiClientOnPrem(BaseAPIClient):
    """The API Client of Access Groups."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = None,
    ) -> None:
        """Initializes the AccessGroupsApiClientOnPrem.

        Args:
            auth: The Authentication object.
            base_url: Default is None.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"usermgmt/v{DEFAULT_ACCESS_GROUP_API_VERSION}/groups"

    def get_all_access_groups(self, params: dict) -> requests.Response:
        """Lists all access groups under an account. Will only list those the listed user can access.

        Args:
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url=url, params=params)
        return response

    def create_access_group(self, data: dict = None) -> requests.Response:
        """Creates a new access group.

        Args:
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.post(url=url, data=data)
        return response

    def update_access_group(self, access_group_id: str, data: dict) -> requests.Response:
        """Updates existing access group.

        Args:
            access_group_id: The access group ID.
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}"
        response = self.patch(url=url, data=data)
        return response

    def delete_access_group(self, access_group_id: str) -> requests.Response:
        """Deletes an access group from an account.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}"
        response = self.delete(url=url)
        return response

    def add_members(self, access_group_id: str, data: dict) -> requests.Response:
        """Adds member(s) to an access group.

        Args:
            access_group_id: The access group ID.
            data: The member(s) to be added to an access group, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}/members"
        response = self.post(url, data=data)
        return response

    def get_members(self, access_group_id: str) -> requests.Response:
        """Lists all members in an access group.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}/members"
        response = self.get(url)
        return response

    def remove_member_from_access_group(self, access_group_id: str, user_id: str) -> requests.Response:
        """Removes multiple members from an access group.

        Args:
            access_group_id: The access group ID.
            user_id: The user ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}/members/{user_id}"
        response = self.delete(url)
        return response
