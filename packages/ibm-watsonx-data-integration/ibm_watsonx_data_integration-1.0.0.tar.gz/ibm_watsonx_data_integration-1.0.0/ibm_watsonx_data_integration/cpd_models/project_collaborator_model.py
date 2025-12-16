#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""Module containing ProjectCollaborator and ProjectCollaborators models."""

from abc import ABC, abstractmethod
from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.common.utils import get_params_from_swagger
from pydantic import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project


class CollaboratorRole(str, Enum):
    """Enum that defines different types of collaborator roles in a project."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class CollaboratorState(str, Enum):
    """Enum that defines different types of collaborator states in a project."""

    ACTIVE = "ACTIVE"
    PENDING = "PENDING"


class CollaboratorType(str, Enum):
    """Enum that defines different types of collaborator types in a project."""

    USER = "user"
    GROUP = "group"
    SERVICE = "service"
    PROFILE = "profile"


class ProjectCollaborator(BaseModel):
    """Class for a collaborator in a project."""

    user_name: str = Field(..., min_length=1, max_length=100, frozen=True, repr=True)
    iam_id: str = Field(..., min_length=0, max_length=100, frozen=True, repr=True, alias="id")
    role: CollaboratorRole = Field(..., frozen=False, repr=True)
    state: CollaboratorState = Field(default=CollaboratorState.ACTIVE, frozen=True, repr=False)
    type: CollaboratorType = Field(default=CollaboratorType.USER, repr=True, frozen=True)

    def __init__(self, project: "Project" = None, **custom_collaborator_json: dict) -> None:
        """The __init__ of a ProjectCollaborator class.

        Args:
            project: The project for the collaborator
            custom_collaborator_json: key word arguments to populate the collaborator object
        """
        super().__init__(**custom_collaborator_json)
        self._project = project


class ProjectCollaborators(CollectionModel):
    """Collection of ProjectCollaborator instances."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the ProjectCollaborators class.

        Args:
            project: the project object
        """
        super().__init__()
        self._project = project
        self.unique_id = "user_name"

    def __len__(self) -> int:
        """Total amount of project collaborators."""
        return len(self._project._platform._project_api.get_project_members(self._project.project_id).json()["members"])

    def _request_parameters(self) -> list:
        request_params = ["project_id"]
        content_string = self._project._platform._project_api.get_swagger().content.decode("utf-8")
        request_path = f"/{self._project._platform._project_api.url_path}/{{project_id}}/members"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns result of an api request."""
        request_params_defaults = {
            "user_names": None,
            "roles": None,
        }

        # if username is in request_params, should just retrieve the single user
        if "user_name" in request_params:
            response = self._project._platform._project_api.get_project_member(
                self._project.project_id, request_params["user_name"]
            ).json()
            response = {"members": [response]}
        else:
            unioned_params = request_params_defaults
            unioned_params.update(request_params)
            response = self._project._platform._project_api.get_project_members(
                project_id=self._project.project_id,
                params={k: v for k, v in unioned_params.items() if v is not None},
            ).json()
        return CollectionModelResults(
            results=response,
            class_type=ProjectCollaborator,
            response_bookmark=None,
            request_bookmark=None,
            response_location="members",
            constructor_params={"project": self._project},
        )


class ProjectCollaboratable(ABC):
    """Interface that indicates a class can be added as a project collaborator."""

    @abstractmethod
    def _to_collaborator(self, project: "Project", role: CollaboratorRole) -> ProjectCollaborator:
        """Returns ProjectCollaborator object."""
        ...
