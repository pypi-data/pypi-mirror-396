#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Configuration Service API client."""

import json
import requests
from ibm_watsonx_data_integration.common.constants import PROD_BASE_URL
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_CONFIG_API_VERSION = 1


class ConfigurationServiceApiClient(BaseAPIClient):
    """The API client of the Config Service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
    ) -> None:
        """The __init__ of the ConfigurationServiceApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/config/v{DEFAULT_CONFIG_API_VERSION}"

    def get_configs(self) -> requests.Response:
        """Get all configuration properties.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/configs"
        response = self.get(url=url)
        return response

    def get_config(self, config_id: str) -> requests.Response:
        """Get a configuration value.

        Args:
            config_id: Configuration config_id.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/configs/{quote(config_id, safe='')}"
        response = self.get(url=url)
        return response

    def patch_config(self, data: dict | str) -> requests.Response:
        """Patch configuration properties.

        Args:
            data: Updated config data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/configs"
        data = json.dumps(data) if isinstance(data, dict) else data
        response = self.patch(url=url, data=data, headers={"Content-Type": "application/merge-patch+json"})
        return response

    def delete_config(self, account_id: str) -> requests.Response:
        """Delete all configurations for an account.

        Args:
            account_id: Id belonging to the account.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/accounts/{quote(account_id, safe='')}"
        response = self.delete(url=url)
        return response
