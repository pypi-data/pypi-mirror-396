#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Configuration Service API client."""

import requests
from ibm_watsonx_data_integration.common.constants import PROD_BASE_URL
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_BROKER_API_VERSION = 2


class BrokerApiClient(BaseAPIClient):
    """The API client of the Broker Client."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
    ) -> None:
        """The __init__ of the BrokerApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/broker/v{DEFAULT_BROKER_API_VERSION}/service_instances"

    def get_status_for_provisioning_instance(self, instance_crn: str, params: dict = None) -> requests.Response:
        """Get status of a provision instance.

        Args:
            instance_crn: Instance crn.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(instance_crn, safe='')}"
        response = self.get(url=url, params=params)
        return response

    def provision_an_instance(self, instance_crn: str, params: dict = None) -> requests.Response:
        """Provision an instance.

        Args:
            instance_crn: Instance crn.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(instance_crn, safe='')}"
        response = self.put(url=url, params=params)
        return response

    def deprovision_an_instance(self, instance_crn: str, params: dict = None) -> requests.Response:
        """Deprovision an instance.

        Args:
            instance_crn: Instance crn.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(instance_crn, safe='')}"
        response = self.delete(url=url, params=params)
        return response

    def update_instance_plan(self, instance_crn: str, params: dict = None) -> requests.Response:
        """Get all configuration properties.

        Args:
            instance_crn: Instance crn.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(instance_crn, safe='')}/plan"
        response = self.post(url=url, params=params)
        return response

    def enable_provision_instance(self, instance_crn: str, params: dict = None) -> requests.Response:
        """Disable or Enable a provisioned instance.

        Args:
            instance_crn: Instance crn.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(instance_crn, safe='')}/state"
        response = self.post(url=url, params=params)
        return response
