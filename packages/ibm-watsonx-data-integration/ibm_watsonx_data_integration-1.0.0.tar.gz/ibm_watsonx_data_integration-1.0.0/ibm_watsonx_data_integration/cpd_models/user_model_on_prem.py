#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Models for User, UserSettings, and Users collection."""

from __future__ import annotations

from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.project_collaborator_model import (
    CollaboratorRole,
    CollaboratorType,
    ProjectCollaboratable,
    ProjectCollaborator,
)
from pydantic import ConfigDict, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform
    from ibm_watsonx_data_integration.cpd_models.project_model import Project


class Authenticator(Enum):
    """Authenticator enum of a group."""

    EXTERNAL = "external"
    INTERNAL = "internal"


class AccountStatus(Enum):
    """AccountStatus enum of a group."""

    ENABLED = "enabled"
    DISABLED = "disabled"


class GroupMisc(BaseModel):
    """Miscellaneous metadata on a group."""

    ext_attributes: dict | None = Field(default=None, repr=False)
    realm_name: str | None = Field(default=None, alias="realm_name", repr=False)
    dark_mode: bool | None = Field(default=None, alias="dark_mode", repr=False)


class Group(BaseModel):
    """Represents a group the user is in."""

    group_id: int = Field(alias="group_id", repr=False)
    name: str = Field(repr=False)
    description: str | None = Field(default=None, repr=False)
    added_separately: bool | None = Field(default=None, alias="added_separately", repr=False)
    created_at: str | None = Field(default=None, alias="created_at", repr=False)
    created_by: str | None = Field(default=None, alias="created_by", repr=False)
    updated_at: str | None = Field(default=None, alias="updated_at", repr=False)
    members_count: int | None = Field(default=None, alias="members_count", repr=False)
    misc: GroupMisc | None = Field(default=None, repr=False)

    model_config = ConfigDict(frozen=True)


class SessionToken(BaseModel):
    """Decoded session token payload (subset modeled to match provided JSON)."""

    aud: str | None = Field(default=None, repr=False)
    iss: str | None = Field(default=None, repr=False)
    sub: str | None = Field(default=None, repr=False)
    uid: int | None = Field(default=None, repr=False)
    role: str | None = Field(default=None, repr=False)
    groups: list[int] | None = Field(default=None, repr=False)
    username: str | None = Field(default=None, repr=False)
    csrf_token: str | None = Field(default=None, alias="csrf_token", repr=False)
    session_id: str | None = Field(default=None, alias="session_id", repr=False)
    api_request: bool | None = Field(default=None, alias="api_request", repr=False)
    permissions: list[str] | None = Field(default=None, repr=False)
    display_name: str | None = Field(default=None, alias="display_name", repr=False)
    authenticator: str | None = Field(default=None, repr=False)
    can_refresh_until: int | None = Field(default=None, alias="can_refresh_until", repr=False)
    iam: dict | None = Field(default=None, repr=False)


class SessionInfo(BaseModel):
    """Represents one active/recorded session for the user."""

    session_id: str = Field(alias="session_id", repr=False)
    created_timestamp: int = Field(alias="created_timestamp", repr=False)
    can_refresh_until: int | None = Field(default=None, alias="can_refresh_until", repr=False)
    misc: dict | None = Field(default=None, repr=False)

    model_config = ConfigDict(frozen=True)


class UserMisc(BaseModel):
    """Per-user miscellaneous metadata."""

    ext_attributes: dict | None = Field(default=None, repr=False)
    realm_name: str | None = Field(default=None, alias="realm_name", repr=False)
    dark_mode: bool | None = Field(default=None, alias="dark_mode", repr=False)
    last_session_start_timestamp: str | int | None = Field(
        default=None, alias="last_session_start_timestamp", repr=False
    )
    last_session_ended_timestamp: str | int | None = Field(
        default=None, alias="last_session_ended_timestamp", repr=False
    )
    session_info: list[SessionInfo] | None = Field(default=None, alias="sessionInfo", repr=False)

    model_config = ConfigDict(frozen=True)


class UserProfileOnPrem(BaseModel, ProjectCollaboratable):
    """Model representing an identity user in the platform."""

    authenticator: Authenticator | str = Field(repr=False)
    created_timestamp: int = Field(repr=False, alias="created_timestamp")
    current_account_status: AccountStatus | str = Field(repr=False, alias="current_account_status")
    deletable: bool = Field(repr=False)
    display_name: str = Field(alias="displayName", repr=True)
    email: str = Field(repr=True)
    group_roles: list[str] = Field(default_factory=list, alias="group_roles", repr=False)
    groups: list[Group] = Field(default_factory=list, repr=False)
    internal_user: bool = Field(alias="internal_user", repr=False)
    last_modified_timestamp: int = Field(alias="last_modified_timestamp", repr=False)
    permissions: list[str] = Field(default_factory=list, repr=False)
    profile_picture: str | None = Field(default=None, repr=False)
    role: str | None = Field(default=None, repr=False)
    user_id: int = Field(frozen=True, repr=True, alias="uid")
    user_roles: list[str] = Field(default_factory=list, alias="user_roles", repr=False)
    username: str = Field(repr=True)
    misc: UserMisc | None = Field(default=None, repr=False)

    model_config = ConfigDict(use_enum_values=True, frozen=True)
    _expose: bool = True

    def __init__(self, platform: Platform | None = None, **user_json: dict) -> None:
        """__init__ for User."""
        super().__init__(**user_json)
        self._platform = platform
        if platform is not None and hasattr(platform, "_user_api"):
            self._identity_api = platform._user_api

    @property
    def type(self) -> str:
        """This property returns the member type "user"."""
        return "user"

    def _to_collaborator(self, project: Project, role: CollaboratorRole) -> ProjectCollaborator:
        """Returns ProjectCollaborator object."""
        return ProjectCollaborator(
            project=project, user_name=self.username, id=str(self.user_id), role=role, type=CollaboratorType.USER
        )


class UserProfilesOnPrem(CollectionModel):
    """Collection of User instances backed by the identity API."""

    def __init__(self, platform: Platform) -> None:
        """__init__ for UserProfilesOnPrem."""
        super().__init__(platform)
        self.unique_id = "user_id"

    def __len__(self) -> int:
        """Return total number of users."""
        params = {}
        res = self._platform._user_api.get_users(params=params)
        res_json = res.json()
        return len(res_json)

    def _request_parameters(self) -> list:
        return ["user_id", "user_ids", "limit", "start", "username"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Fetch and normalize results."""
        if (
            "_start" in request_params
            and isinstance(request_params["_start"], str)
            and "_start=" in request_params["_start"]
        ):
            request_params["_start"] = request_params["_start"].split("_start=")[1].split("&")[0]

        request_params_defaults = {
            "limit": None,
            "_start": None,
        }

        request_params_unioned = request_params_defaults.copy()
        request_params_unioned.update(request_params)

        user_id = request_params_unioned.get("user_id")
        user_ids = request_params_unioned.get("user_ids")
        username = request_params_unioned.get("username")

        if "user_id" in request_params_unioned:
            response_json = self._platform._user_api.get_user(user_id=user_id, params={}).json()
            response_json = {"resources": [response_json]}
        elif "user_ids" in request_params_unioned:
            response_json = self._platform._user_api.get_users_by_id(user_ids=",".join(user_ids)).json()
            response_json = {"resources": response_json["users"]}
        elif "username" in request_params_unioned:
            response_json = self._platform._user_api.get_user_by_username(username=username).json()
            response_json = {"resources": [response_json]}
        else:
            response_json = self._platform._user_api.get_users(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
            response_json = {"resources": response_json}

        return CollectionModelResults(
            response_json,
            UserProfileOnPrem,
            "next_url",
            "_start",
            "resources",
            {"platform": self._platform},
        )
