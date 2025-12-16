#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Streaming Flow API client."""

import requests
from ibm_watsonx_data_integration.common.utils import wait_and_retry_on_http_error
from ibm_watsonx_data_integration.cpd_api.adapters import DefaultHTTPAdapter
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

FLOWSTORE_API_VERSION = 1


class StreamingFlowApiClient(BaseAPIClient):
    """The API client of the Streaming Flows."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
    ) -> None:
        """The __init__ of the StreamingFlowApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Streaming Flow URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/streamsets_flows/v{FLOWSTORE_API_VERSION}"
        self.url_path_connections = f"sset/streamsets_flows/v{FLOWSTORE_API_VERSION}/connections"

    @wait_and_retry_on_http_error(timeout_sec=10)
    def get_streaming_flows(self, params: dict) -> requests.Response:
        """Get all Streaming Flows.

        Args:
           params: The Query params.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows"
        response = self.get(url=url, params=params)
        return response

    def get_streaming_flow_by_id(self, params: dict, flow_id: str) -> requests.Response:
        """Get all Streaming Flows by id.

        Args:
            params: The Query params.
            flow_id: The Flow ID.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.get(url=url, params=params)
        return response

    def delete_streaming_flow(self, params: dict, flow_id: str) -> requests.Response:
        """Delete a Streaming Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.delete(url=url, params=params)
        return response

    def update_streaming_flow(self, params: dict, flow_id: str, data: str) -> requests.Response:
        """Update a Streaming Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.
            data: The payload data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.put(url=url, data=data, params=params)
        return response

    @wait_and_retry_on_http_error(timeout_sec=4)
    def create_streaming_flow(self, params: dict, data: str) -> requests.Response:
        """Create a Streaming Flow.

        Args:
            params: The Query params.
            data: The payload data.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows"
        response = self.post(url=url, data=data, params=params)
        return response

    @wait_and_retry_on_http_error(timeout_sec=4)
    def duplicate_streaming_flow(self, params: dict, flow_id: str, data: str) -> requests.Response:
        """Duplicate a Streaming Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.
            data: The payload data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}/duplicate"
        response = self.post(url=url, data=data, params=params)
        return response

    @wait_and_retry_on_http_error(timeout_sec=4)
    def export_streaming_flow(self, params: dict, stream: bool) -> requests.Response:
        """Export Streaming Flows.

        Args:
            params: The Query params.
            stream: Whether to stream the response in chunks.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/export/flows"
        response = self.get(url=url, params=params, stream=stream)
        return response

    def import_streaming_flow(self, params: dict, data: str) -> requests.Response:
        """Import Streaming Flows.

        Args:
            params: The Query params.
            data: The zipfile data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/import/flows"

        adapter = DefaultHTTPAdapter(auth=self._auth)
        adapter._custom_headers["Content-Type"] = "application/octet-stream"

        response = self.post(url=url, params=params, data=data, adapter=adapter)
        return response

    def get_streaming_connection(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Get streaming connection.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}"
        return self.get(url=url, params=params)

    def get_streaming_connections(self, params: dict[str, Any]) -> requests.Response:
        """List defined Streaming connections.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}"
        return self.get(url=url, params=params)
