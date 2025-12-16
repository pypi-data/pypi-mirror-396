#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Project API client."""

import json
import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_PROJECTS_API_VERSION = 2


class ProjectApiClient(BaseAPIClient):
    """The API client of the Project."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
    ) -> None:
        """The __init__ of the ProjectApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_PROJECTS_API_VERSION}/projects"

    def get_projects(self, params: dict = None) -> requests:
        """Get all Projects.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url=url, params=params)
        return response

    def get_project(self, id: str) -> requests.Response:
        """Get a Project.

        Args:
            id: Project ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}"
        params = {"include": "name,fields,members,tags,settings"}
        response = self.get(url=url, params=params)
        return response

    def create_project(self, data: str) -> requests.Response:
        """Create a Project.

        Args:
            data: Project JSON String.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/transactional/{self.url_path}"
        response = self.post(url=url, data=data)
        return response

    def get_projects_total(self, params: dict = None) -> requests.Response:
        """Total number of projects.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/total"
        response = self.get(url=url, params=params)
        return response

    def delete_project(self, id: str) -> requests.Response:
        """Delete a Project.

        Args:
            id: Project ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/transactional/{self.url_path}/{quote(id, safe='')}"
        response = self.delete(url=url)
        return response

    def update_project(self, id: str, data: str) -> requests.Response:
        """Update a Project.

        Args:
            id: Project ID.
            data: Project JSON String.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}"
        response = self.patch(url=url, data=data)
        return response

    def get_tags(self, id: str) -> requests.Response:
        """Get tags for a Project.

        Args:
            id: Project ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags"
        response = self.get(url=url)
        return response

    def update_tags(self, id: str, data: str) -> requests.Response:
        """Update a Project.

        Args:
            id: Project ID.
            data: The tags payload.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags"
        response = self.patch(url=url, data=data)
        return response

    def add_tags(self, id: str, tags: list) -> requests.Response:
        """Add tags for a Project.

        Args:
            id: Project ID.
            tags: The tags list.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags"
        response = self.post(url=url, data=tags)
        return response

    def delete_tags(self, id: str, tags: list) -> requests.Response:
        """Delete tags for a Project.

        Args:
            id: Project ID.
            tags: The Tag JSON.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags"
        params = {"include": tags}
        response = self.delete(url=url, params=params)
        return response

    def add_tag(self, id: str, tag: str) -> requests.Response:
        """Add a tag to a Project.

        Args:
            id: Project ID.
            tag: The Tag JSON.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags/{quote(tag, safe='')}"
        response = self.post(url=url)
        return response

    def delete_tag(self, id: str, tag: str) -> requests.Response:
        """Delete a tag for a Project.

        Args:
            id: Project ID.
            tag: The Tag JSON.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(id, safe='')}/tags/{quote(tag, safe='')}"
        response = self.delete(url=url)
        return response

    def get_swagger(self) -> requests.Response:
        """Retrieve the swagger definitions to retrieve projects.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/docs/schemas/v2-projects-api-openapi.yml"
        response = self.get(url=url)
        return response

    def get_batch_environments(self) -> requests.Response:
        """Retreive batch environments in project.

        Returns:
            A HTTP response.
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        headers["Accept"] = "application/json"

        url = "/v2/environments"
        params = {"project_id": "b4b08013-c3a2-46a5-b559-db94a46b7039", "types": "datastage"}
        return self.get(url=url, headers=headers, params=params)

    def get_project_members(self, project_id: str, params: dict = None) -> requests.Response:
        """Retrieves list of members in the project.

        Args:
            project_id: id of the project
            params: query parameters to filter results by

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(project_id, safe='')}/members"
        headers = {"agentname": "watsonx-di-sdk"}
        return self.get(url=url, headers=headers, params=params)

    def get_project_member(self, project_id: str, user_name: str) -> requests.Response:
        """Retrieves a single member from a project based on the user_name.

        Args:
            project_id: id of the project
            user_name: username of the member to retrieve

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(project_id, safe='')}/members/{quote(user_name, safe='')}"
        headers = {"agentname": "watsonx-di-sdk"}
        return self.get(url=url, headers=headers)

    def add_project_members(self, project_id: str, members: list[str]) -> requests.Response:
        """Adds a list of members to a project.

        Args:
            project_id: id of the project
            members: list of members to add, (dumped ProjectCollaborator objects)

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(project_id, safe='')}/members"
        headers = {"agentname": "watsonx-di-sdk", "Content-Type": "application/json"}
        data = json.dumps({"members": members})
        return self.post(url=url, headers=headers, data=data)

    def remove_project_members(self, project_id: str, user_names: list[str]) -> requests.Response:
        """Removes a list of members from a project.

        Args:
            project_id: id of the project
            user_names: list of user names to remove

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(project_id, safe='')}/members"
        headers = {"agentname": "watsonx-di-sdk"}
        params = {"user_names": ",".join(user_names)}
        return self.delete(url=url, headers=headers, params=params)

    def update_project_members(self, project_id: str, members: list[str]) -> requests.Response:
        """Updates a list of members in a project.

        Args:
            project_id: id of the project
            members: list of members to add, (dumped ProjectCollaborator objects without type field)

        Returns:
            requests.Response: _description_
        """
        url = f"{self.base_url}/{self.url_path}/{quote(project_id, safe='')}/members"
        headers = {"agentname": "watsonx-di-sdk", "Content-Type": "application/json"}
        data = json.dumps({"members": members})
        return self.patch(url=url, headers=headers, data=data)
