#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing AccessGroupOnPrem Model."""

from __future__ import annotations

import json
import requests
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.project_collaborator_model import (
    CollaboratorRole,
    CollaboratorType,
    ProjectCollaboratable,
    ProjectCollaborator,
)
from pydantic import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.role_model_on_prem import RoleOnPrem
    from ibm_watsonx_data_integration.platform import Platform
    from ibm_watsonx_data_integration.cpd_models.project_model import Project


class AccessGroupOnPrem(BaseModel, ProjectCollaboratable):
    """On-prem Access Group model."""

    group_id: int | str = Field(frozen=True, repr=True)
    name: str = Field(repr=True)
    description: str = Field(default=None)
    created_at: str = Field(repr=False)
    created_by: str = Field(repr=False)
    updated_at: str = Field(repr=False)
    misc: dict = Field(default_factory=dict, repr=False)
    roles: list[dict] = Field(default_factory=list, repr=False)
    permissions: list[str] = Field(default_factory=list, repr=False)
    members_count: int = Field(default=0, repr=True)

    def __init__(self, platform: Platform | None = None, **group_json: dict) -> None:
        """The __init__ of the AccessGroup class."""
        super().__init__(**group_json)
        self._platform = platform

    @staticmethod
    def _create(
        platform: Platform, name: str, description: str | None = None, roles: list[RoleOnPrem] | None = []
    ) -> AccessGroupOnPrem:
        """Create the AccessGroup object."""
        data = {
            "name": name,
            "description": description,
            "account_id": platform.current_on_prem_user.user_id,
            "role_identifiers": [role.role_id for role in roles],
        }
        data = json.dumps(data)
        response = platform._access_group_api.create_access_group(data=data)
        access_group_json = response.json()
        return AccessGroupOnPrem(platform=platform, **access_group_json)

    def _update(self) -> requests.Response:
        """Update the AccessGroup object."""
        data = {
            "name": self.name,
            "description": self.description,
            "account_id": self._platform.current_on_prem_user.user_id,
            "add_role_identifiers": [],
            "remove_role_identifiers": [],
        }
        data = json.dumps(data)

        response = self._platform._access_group_api.update_access_group(access_group_id=self.group_id, data=data)

        return response

    def _delete(self) -> requests.Response:
        """Delete the AccessGroup object."""
        return self._platform._access_group_api.delete_access_group(self.group_id)

    def add_members_to_access_group(self, users: list[object]) -> requests.Response:
        """Adds members to an AccessGroup.

        Args:
            users: The members to be added to the access group.

        Returns:
            A HTTP response.
        """
        user_ids = [user.user_id for user in users]
        data = json.dumps({"user_identifiers": user_ids})

        return self._platform._access_group_api.add_members(self.group_id, data)

    def remove_member_from_access_group(self, user: object) -> requests.Response:
        """Removes members from access group.

        Args:
            user: Member to be removed from access group.

        Returns:
            A HTTP response.
        """
        return self._platform._access_group_api.remove_member_from_access_group(self.group_id, user.user_id)

    def _to_collaborator(self, project: Project, role: CollaboratorRole) -> ProjectCollaborator:
        """Returns ProjectCollaborator object."""
        return ProjectCollaborator(
            project=project,
            user_name=str(self.group_id),
            id=str(self.group_id),
            role=role,
            type=CollaboratorType.GROUP,
        )


class AccessGroupsOnPrem(CollectionModel):  # name matches your requested spelling
    """Collection of AccessGroupOnPrem instances."""

    def __init__(self, platform: Platform | None = None) -> None:
        """The __init__ of the AccessGroupsOnPrem class."""
        super().__init__(platform)
        self.unique_id = "group_id"

    def __len__(self) -> int:
        """Total amount of on-prem access groups.

        Expect either a list payload or an envelope with 'groups' + 'total_count'.
        """
        resp = self._platform._access_group_api.get_all_access_groups(params={"include_members": "false"})
        body = resp.json()
        return len(body)

    def _request_parameters(self) -> list:
        return [
            "group_id",
            "limit",
        ]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an API request, normalizing different possible shapes."""
        request_params_defaults = {
            "group_identifiers": None,
            "role_identifiers": None,
            "include_members": "true",
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        group_id = request_params_unioned.get("group_id")

        if group_id:
            request_params_unioned["group_identifiers"] = [group_id]

        response = self._platform._access_group_api.get_all_access_groups(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            AccessGroupOnPrem,
            "next",
            "_start",
            "results",
            {"platform": self._platform},
        )
