#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""This module contains the UserAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_USER_API_VERSION = 1


class UserAPIClientOnPrem(BaseAPIClient):
    """The API client of the User service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str,
    ) -> None:
        """Initializes the UserAPIClient.

        Args:
            auth: The Authentication object.
            base_url: The User Service URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"/usermgmt/v{DEFAULT_USER_API_VERSION}"

    def get_users(self, params: dict = None) -> requests.Response:
        """Retrieve a list of users.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/usermgmt/users"
        response = self.get(url=url, params=params)
        return response

    def get_user(self, user_id: str, params: dict = None) -> requests.Response:
        """Retrieve a user.

        Args:
            user_id: Unique identifier of the account.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/usermgmt/user/{user_id}"
        response = self.get(url=url, params=params)
        return response

    def get_user_by_username(self, username: str) -> requests.Response:
        """Retrieve a user by name.

        Args:
            username: Username of the user.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/user/{username}"
        response = self.get(url=url)
        return response

    def get_users_by_id(self, user_ids: str) -> requests.Response:
        """Retrieve a list of users by ID.

        Args:
            user_ids: User IDs.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/users"
        params = {"uids": user_ids}
        response = self.get(url=url, params=params)
        return response

    def delete_user(self, username: str) -> requests.Response:
        """Remove a user.

        Args:
            username: Username of the user.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/user/{username}"
        response = self.delete(url=url)
        return response

    def update_user(self, username: str, data: dict) -> requests.Response:
        """Update the settings for a specific user in an account.

        Args:
            username: Username of the user.
            data: Dictionary containing any or all settings to update. For example:
                {
                    "language": "en-us",
                    "notification_language": "en-us",
                    "allowed_ip_addresses": "32.96.110.50,172.16.254.1",
                    "self_manage": True,
                    "2FA": False,
                    "security_questions_required": False,
                    "security_questions_setup": False
                }

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/user/{username}"
        response = self.put(url=url, data=data)
        return response
