#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Parameter Set and Parameter Models."""

from __future__ import annotations

import requests
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Any, ClassVar
from typing_extensions import override
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project

_ALLOWED_PARAM_TYPES = [
    "date",
    "email",
    "encrypted",
    "float",
    "integer",
    "list",
    "multilinestring",
    "path",
    "string",
    "time",
    "timestamp",
    "sfloat",
    "enum",
    "int64",
]


class ValueSet(BaseModel):
    """Class for a value set for a parameter set."""

    name: str
    values: list[dict[str, Any]] = []  # noqa: ANN401

    def add_value(self, name: str, value: Any) -> ValueSet:  # noqa: ANN401
        """Add or replace value in ValueSet."""
        for value_dict in self.values:
            if value_dict["name"] == name:
                value_dict["value"] = value
                return self
        self.values.append({"name": name, "value": value})
        return self

    def remove_value(self, name: str) -> ValueSet:
        """Remove value from ValueSet."""
        self.values = [value for value in self.values if value["name"] != name]
        return self


class Parameter(BaseModel):
    """Class for a parameter in a parameter set."""

    name: str
    param_type: str = Field(alias="type")
    description: str | None = None
    prompt: str | None = None
    value: Any | None = None
    valid_values: list[Any] | None = []

    def _to_local_parameter(self) -> dict:
        return {
            "prompt": self.prompt,
            "value": self.value,
            "name": self.name,
            "suptype": getattr(self, "subtype", ""),
            "type": self.param_type,
        }


class ParameterSetMetadata(BaseModel):
    """Metadata for a parameter set."""

    asset_category: str | None = Field(None, description='The asset category ("USER" or "SYSTEM")', repr=False)
    asset_id: str | None = Field(None, description="The ID of the asset", repr=False)
    asset_type: str | None = Field(None, description="The type of the asset", repr=False)
    catalog_id: str | None = Field(
        None,
        description="The ID of the catalog which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    create_time: str | None = Field(
        None,
        description="The timestamp when the asset was created",
        repr=False,
    )
    creator_id: str | None = Field(None, description="The IAM ID of the user that created the asset", repr=False)
    href: str | None = Field(None, description="URL that can be used to get the asset.", repr=False)
    owner_id: str | None = Field(None, description="The IAM ID of the user that owns the asset", repr=False)
    project_id: str | None = Field(
        None,
        description="The ID of the project which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    resource_key: str | None = Field(
        None, description="Optional external unique key for assets that supports it", repr=False
    )
    space_id: str | None = Field(
        None,
        description="The ID of the space which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    tags: list[str] | None = Field(None, repr=False)


class ParameterSet(BaseModel):
    """A parameter set consists of a name, a list of parameters, a list of value sets, and a description.

    Args:
        name: (*Required*) The name of the parameter set.
        parameters: A list of Parameter objects.
        description: An optional description of the parameter set.
        value_sets: A list of ValueSet objects.
    """

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.parameter_set": {}}
    metadata: ParameterSetMetadata | None = Field(None, repr=False)

    parameter_set_id: str | None = Field(
        repr=False,
        default_factory=lambda fields: fields["metadata"].asset_id if fields["metadata"] else None,
        description="Returns id of parameter set",
        exclude=True,
        frozen=True,
    )
    name: str = Field(description="The name of the parameter set.", repr=True)
    parameters: list[Parameter] = Field(
        default_factory=list, description="The parameters in a parameter set", repr=True
    )
    description: str | None = Field("", description="The description of the parameter set", repr=True)
    value_sets: list[ValueSet] = Field(default_factory=list, description="The value sets of a parameter set", repr=True)

    def __init__(self, project: Project = None, **parameter_set_json: dict) -> None:  # noqa: ANN401, D417
        """The __init__ of the ParameterSet class.

        Args:
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(**parameter_set_json)
        if project:
            self._project = project

    def __getitem__(self, parameter: str) -> str:
        """Get parameter from parameter set by name."""
        for param in self.parameters:
            if param.name == parameter:
                return f"#{self.name}.{param.name}#"
        raise ValueError(f"Parameter {parameter} does not exist in set {self.name}")

    def __contains__(self, parameter: str) -> bool:
        """Check if parameter is in the parameter set by name."""
        for param in self.parameters:
            if param.name == parameter:
                return True
        return False

    def add_parameter(
        self,
        parameter_type: str,
        name: str,
        description: str | None = None,
        prompt: str | None = None,
        value: Any | None = None,  # noqa: ANN401
        valid_values: list[Any] | None = [],  # noqa: ANN401
    ) -> ParameterSet:
        """Adds a Parameter to the parameter set.

        Args:
            parameter_type: Parameter type.
            name: Parameter name.
            description: Parameter help text.
            prompt: Parameter prompt
            value: Parameter value
            valid_values: Valid values for List Parameter only.

        Returns:
            The ParameterSet object with an updated list of parameters.
        """
        parameter_type = parameter_type.lower()
        if parameter_type in _ALLOWED_PARAM_TYPES:
            if parameter_type == "list":
                if not valid_values:
                    raise ValueError("Valid values must be provided")
                new_param = Parameter(
                    name=name,
                    description=description,
                    prompt=prompt,
                    value=value,
                    valid_values=valid_values,
                    type="enum",
                )
            elif parameter_type == "integer":
                new_param = Parameter(
                    name=name,
                    description=description,
                    prompt=prompt,
                    value=value,
                    type="int64",
                    valid_values=None,
                )
            else:
                new_param = Parameter(
                    name=name,
                    description=description,
                    prompt=prompt,
                    value=value,
                    type=parameter_type,
                    valid_values=None,
                )
            self.parameters.append(new_param)
            return self
        else:
            raise ValueError(f"Unsupported param type: {parameter_type}. Supported types are: {_ALLOWED_PARAM_TYPES}")

    def remove_parameter(self, parameter_name: str) -> ParameterSet:
        """Removes a parameter from the parameter set.

        Args:
            parameter_name: Name of the parameter to remove

        Returns:
            The ParameterSet object with an updated list of parameters.
        """
        self.parameters = [parameter for parameter in self.parameters if parameter.name != parameter_name]
        return self

    @staticmethod
    def _create(
        project: Project, name: str, description: str, parameters: list = None, value_sets: list = None
    ) -> ParameterSet:
        properties = {}
        properties["name"] = name
        properties["description"] = description
        properties["parameters"] = parameters or []
        properties["value_sets"] = value_sets or []
        response = project._platform._parameter_set_api_client.create_parameter_set(
            parameter_set=properties, project_id=project.project_id
        )
        return ParameterSet(
            project=project,
            **response.json(),
        )

    def _update(self) -> requests.Response:
        properties = self.model_dump(
            exclude_none=True, exclude=["metadata", "project_id"], by_alias=True, warnings=False
        )
        patch_request = [
            {
                "op": "replace",
                "path": "/entity/parameter_set",
                "value": properties["entity"]["parameter_set"],
            }
        ]
        return self._project._platform._parameter_set_api_client.patch_parameter_set(
            parameter_set_patch_entity=patch_request,
            parameter_set_id=self.metadata.asset_id,
            project_id=self._project.project_id,
        )

    def _delete(self) -> requests.Response:
        return self._project._platform._parameter_set_api_client.delete_parameter_sets(
            id=[self.parameter_set_id], project_id=self._project.project_id
        )

    def _duplicate(self) -> ParameterSet:
        response = self._project._platform._parameter_set_api_client.clone_parameter_set(
            parameter_set_id=self.metadata.asset_id, project_id=self._project.project_id
        )
        return ParameterSet(
            project=self._project,
            **response.json(),
        )

    def add_value_set(self, value_set: ValueSet) -> ParameterSet:
        """Adds a ValueSet to the list of value sets.

        Args:
            value_set: (*Required*) A ValueSet object.

        Returns:
            The ParameterSet object with an updated list of value_sets.
        """
        found_names = []
        for value in value_set.values:
            found = False
            for param in self.parameters:
                if value["name"] == param.name:
                    found_names.append(param.name)
                    found = True
                    break
            if not found:
                raise ValueError(f"Parameter {value['name']} is not present in parameter set")

        for param in self.parameters:
            if param.name not in found_names:
                value_set.add_value(param.name, param.value)
        self.value_sets.append(value_set)
        return self

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

    @classmethod
    def from_dict(cls, dict: dict[str, Any]) -> ParameterSet:
        """Creates a new ParameterSet object from a dictionary of values.

        Args:
            dict: A dictionary of values for a ParameterSet object.

        Returns:
            A new ParameterSet object with the existing parameter set details.
        """
        parameters = dict.get("parameters")
        param_objects = []
        if parameters:
            for param in parameters:
                param_type = param.get("type")
                if "int" in param_type:
                    param_type = "integer"
                name = param.get("name")
                value = param.get("value")
                description = param.get("description")
                # subtype = param.get("subtype")
                valid_values = param.get("valid_values")
                if param_type == "sfloat":
                    param_objects.append(
                        Parameter(
                            name=name,
                            value=value,
                            description=description,
                            type="float",
                        )
                    )
                elif param_type == "enum":
                    param_objects.append(
                        Parameter(
                            name=name, value=value, description=description, type=param_type, valid_values=valid_values
                        )
                    )
                else:
                    param_objects.append(
                        Parameter(
                            name=name,
                            value=value,
                            description=description,
                            type=param_type,
                        )
                    )

        name = dict.get("name")
        description = dict.get("description")
        # value_sets = dict.get("value_sets") or []
        value_sets = []
        asset_id = dict.get("asset_id")
        proj_id = dict.get("proj_id")
        formatted_dict = {
            "platform": None,
            "project": None,
            "name": name,
            "parameters": param_objects,
            "description": description,
            "value_sets": value_sets,
            "metadata": {"asset_id": asset_id},
            "proj_id": proj_id,
        }
        return cls(**formatted_dict)

    def _to_external_parameter(self) -> dict:
        return {
            "name": self.name,
            "description": self.description if self.description else "",
            "ref": self.parameter_set_id,
            "project_id": self.metadata.project_id,
        }


class ParameterSets(CollectionModel):
    """Collection of ParameterSet instances."""

    def __init__(self, project: Project) -> None:
        """The __init__ of the ParameterSets class.

        Args:
            project: Instance of Project in which parameter set was created.
        """
        super().__init__()
        self.unique_id = "parameter_set_id"
        self._project = project

    @override
    def __len__(self) -> int:
        parametersets_json = self._project._platform._parameter_set_api_client.get_parameter_sets(
            project_id=self._project.project_id
        ).json()
        return parametersets_json["total_count"]

    def _request_parameters(self) -> list:
        return [
            "parameter_set_id",
            "project_id",
            "sort",
            "start",
            "limit",
            "entity.parameter_set.name",
            "entity.parameter_set.description",
            "entity.parameter_set.parameters",
            "entity.parameter_set.value_sets",
        ]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "start" in request_params:
            parsed_url = urlparse(request_params["start"]["href"])
            params = parse_qs(parsed_url.query)
            request_params["start"] = params.get("start", [None])[0]

        request_params_defaults = {
            "parameter_set_id": None,
            "project_id": self._project.metadata.guid,
            "sort": None,
            "start": None,
            "limit": 100,
            "entity.parameter_set.name": None,
            "entity.parameter_set.description": None,
            "entity.parameter_set.parameters": None,
            "entity.parameter_set.value_sets": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        if "entity.parameter_set.name" in request_params_unioned:
            request_params_unioned["entity_name"] = request_params_unioned.get("entity.parameter_set.name")
        if "entity.parameter_set.description" in request_params_unioned:
            request_params_unioned["entity_description"] = request_params_unioned.get(
                "entity.parameter_set.description"
            )
        if "parameter_set_id" in request_params:
            response_json = self._project._platform._parameter_set_api_client.get_parameter_set(
                **{k: v for k, v in request_params_unioned.items() if v is not None},
            ).json()
            response = {"parameter_sets": [response_json]}

        else:
            response = self._project._platform._parameter_set_api_client.get_parameter_sets(
                **{k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
        # Create parameters for construction
        for paramset_json in response["parameter_sets"]:
            paramset_json["parameter_set_id"] = paramset_json["metadata"]["asset_id"]
            paramset_json["name"] = paramset_json["metadata"]["name"]
            paramset_json["description"] = paramset_json["metadata"]["description"]

        return CollectionModelResults(
            results=response,
            class_type=ParameterSet,
            response_bookmark="next",
            request_bookmark="start",
            response_location="parameter_sets",
            constructor_params={"project": self._project},
        )
