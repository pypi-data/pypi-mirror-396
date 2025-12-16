#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""On-prem Roles models."""

from __future__ import annotations

import json
import logging
import requests
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform

logger = logging.getLogger(__name__)


class RoleOnPrem(BaseModel):
    """On-prem Role model."""

    role_id: str = Field(frozen=True, repr=True, alias="id")
    extension_id: str | None = Field(default=None, repr=False)
    extension_name: str | None = Field(default=None, repr=False)
    role_name: str = Field(repr=True)
    description: str | None = Field(default=None, repr=False)
    permissions: list[str] = Field(default_factory=list, repr=False)
    updated_at: int | None = Field(frozen=True, default=None, repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"doc": {}}

    def __init__(self, platform: Platform | None = None, **role_json: dict) -> None:
        """__init__ for On-prem Role model."""
        super().__init__(**role_json)
        self._platform = platform

    @staticmethod
    def _create(platform: Platform, name: str, permissions: list[str], description: str) -> RoleOnPrem:
        """Create an on-prem Role model."""
        data = {
            "role_name": name,
            "description": description,
            "permissions": permissions,
        }

        response = platform._role_api.create_role(json.dumps(data))
        response_json = response.json()
        return platform.roles.get(role_id=response_json["id"])

    def _update(self) -> requests.Response:
        """Update on-prem role."""
        data = {
            "role_name": self.role_name,
            "description": self.description,
            "permissions": self.permissions,
        }

        return self._platform._role_api.update_role(self.role_id, data=json.dumps(data))

    def _delete(self) -> requests.Response:
        """Delete on-prem role."""
        return self._platform._role_api.delete_role(self.role_id)


class RolesOnPrem(CollectionModel):
    """Collection of on-prem roles."""

    def __init__(self, platform: Platform) -> None:
        """__init__ of RolesOnPrem."""
        super().__init__(platform=platform)
        self.unique_id = "role_id"

    def __len__(self) -> int:
        """__len__ of RolesOnPrem."""
        resp = self._platform._role_api.get_roles(params={})
        body = resp.json()
        return len(body["rows"])

    def _request_parameters(self) -> list:
        """_request_parameters of RolesOnPrem."""
        return ["limit"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "include_users_count": "true",
            "include_platform_users_count": "true",
            "include_user_groups_count": "true",
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        if request_params:
            request_params_unioned.update(request_params)

        response = self._platform._role_api.get_roles(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()

        return CollectionModelResults(
            response,
            RoleOnPrem,
            "",
            "",
            "rows",
            constructor_params={"platform": self._platform},
        )
