"""Subflow."""

import copy
import json
import requests
from collections.abc import Iterator
from ibm_watsonx_data_integration.common.models import CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.parameter_set_model import Parameter, ParameterSet
from ibm_watsonx_data_integration.services.datastage.models.extractor import SubflowExtractor
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import DAG, EntryNode, ExitNode, SuperNode
from ibm_watsonx_data_integration.services.datastage.models.flow_stages import FlowComposer
from ibm_watsonx_data_integration.services.datastage.models.layout import LayeredLayout
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project

_ALLOWED_PARAM_TYPES_FOR_SUBFLOW = [
    "date",
    "float",
    "integer",
    "path",
    "string",
    "time",
    "sfloat",
]


class Subflow(FlowComposer, SuperNode):
    """Represents a batch subflow."""

    def __init__(
        self,
        dag: DAG = None,
        name: str = "unnamed_subflow",
        is_local: bool = None,
        asset_id: str = None,
        description: str = "",
        project: "Project" = None,
        parameter_sets: list = [],
        parent_dag: DAG = None,
        label: str = None,
        pipeline_id: str = None,
        url: str = None,
        local_parameters: list[Parameter] = [],
        local_parameter_values: dict[str, str] = {},
        **kwargs,  # noqa: ANN003
    ) -> None:
        """Initializer for subflow."""
        self._disabled = False

        if dag is None:
            dag = DAG()

        FlowComposer.__init__(self, dag)

        self.parameter_sets = parameter_sets or []
        self.local_parameters = local_parameters or []
        self._local_parameter_values = local_parameter_values or {}
        self.description = description
        self._project = project
        self.asset_id = asset_id

        SuperNode.__init__(
            self,
            subflow_dag=self._dag,
            name=name,
            is_local=is_local,
            label=label,
            parent_dag=parent_dag,
            pipeline_id=pipeline_id,
            url=url,
        )

    def __repr__(self) -> str:
        """Returns representation of subflow object."""
        if self.label:
            return f"Subflow(label='{self.label}', name='{self.name}', description='{self.description}')"
        return f"Subflow(name='{self.name}', description='{self.description}')"

    def _delete(self) -> requests.Response:
        return self._project._platform._batch_flow_api.delete_batch_subflows(
            id=[self.asset_id],
            project_id=self._project.metadata.guid,
        )

    def _load_pipeline_id(self) -> dict:
        # need to get primary pipeline id in order to properly serialize the subflow when used in a flow
        # unfortunately this is not returned when creating the flow
        get_response = self._project._platform._batch_flow_api.get_batch_subflows(
            project_id=self._project.metadata.guid, data_intg_subflow_id=self.asset_id
        ).json()
        self.pipeline_id = get_response["attachments"]["primary_pipeline"]
        return get_response

    def _create(self) -> "Subflow":
        response = self._project._platform._batch_flow_api.create_batch_subflows(
            data_intg_subflow_name=self.name,
            pipeline_flows=json.loads(self._to_json()),
            project_id=self._project.metadata.guid,
        ).json()

        subflow_obj = Subflow(
            project=self._project,
            name=self.name,
            description=self.description,
            asset_id=response["metadata"]["asset_id"],
            is_local=self.is_local,
            dag=self._dag,
            parameter_sets=self.parameter_sets,
            url=response["metadata"]["href"],
            label=self.label,
        )

        subflow_obj._load_pipeline_id()
        return subflow_obj

    def _update(self) -> requests.Response:
        response = self._project._platform._batch_flow_api.update_batch_subflows(
            data_intg_subflow_id=self.asset_id,
            data_intg_subflow_name=self.name,
            pipeline_flows=json.loads(self._to_json()),
            project_id=self._project.metadata.guid,
        )

        self._load_pipeline_id()
        return response

    def _duplicate_external(self, name: str, description: str) -> "Subflow":
        response = self._project._platform._batch_flow_api.clone_batch_subflows(
            data_intg_subflow_id=self.asset_id,
            data_intg_subflow_name=name,  # New name
            project_id=self._project.metadata.guid,
        )

        subflow_obj = Subflow(
            project=self._project,
            name=name,  # New name
            description=description,  # New description
            asset_id=response.json()["metadata"]["asset_id"],
            is_local=self.is_local,
            dag=self._dag,
            parameter_sets=self.parameter_sets,
        )

        return subflow_obj

    def _duplicate_local(self, name: str) -> "Subflow":
        subflow = Subflow(
            dag=copy.deepcopy(self._dag),
            project=self._project,
            name=name,
            is_local=True,
            parameter_sets=self.parameter_sets,
        )

        for node in list(subflow.entry_nodes) + list(subflow.exit_nodes):
            subflow._dag.remove_node(node)

        return subflow

    def _duplicate(self, name: str, description: str) -> "Subflow":
        if not self.is_local:
            return self._duplicate_external(name, description)
        else:
            return self._duplicate_local(name)

    @staticmethod
    def _blank_json(name: str = "", description: str = "") -> dict:
        return {
            "doc_type": "subpipeline",
            "version": "3.0",
            "json_schema": "https://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json",
            "id": "",
            "primary_pipeline": "",
            "pipelines": [
                {
                    "id": "",
                    "description": description,
                    "runtime_ref": "",
                    "nodes": [],
                    "app_data": {"ui_data": {"comments": []}},
                }
            ],
            "schemas": [],
            "app_data": {"datastage": {}},
            "name": name,
        }

    def _to_json(self) -> str:
        def _compute_local_supernode_metadata(node: SuperNode) -> None:
            node._dag.compute_metadata()
            sub_lay = LayeredLayout(node._dag)
            sub_lay.compute()

            for sub_node in node._dag.nodes():
                if isinstance(sub_node, SuperNode) and sub_node.is_local:
                    _compute_local_supernode_metadata(sub_node)

        if not self._dag or not self._dag.adj:
            return json.dumps(Subflow._blank_json(self.name, self.description))

        self._dag.compute_metadata()
        lay = LayeredLayout(self._dag)
        lay.compute()

        for node in self._dag.nodes():
            if isinstance(node, SuperNode) and node.is_local:
                _compute_local_supernode_metadata(node)

        ser = SubflowExtractor(self._dag, self.parameter_sets, self.local_parameters)
        ser.extract()

        subflow_model = ser.serialize()
        # print(subflow_model.model_dump_json(indent=2, exclude_none=True, by_alias=True, warnings=False))
        return subflow_model.model_dump_json(indent=2, exclude_none=True, by_alias=True, warnings=False)

    def _disable(self) -> None:
        """Disables subflow after deconstruction so it cannot be used."""
        self._disabled = True

    def __getattribute__(self, name: str) -> object:
        """Prevents getting attributes from subflow after it is disabled."""
        if name not in {"_disabled", "disable", "__repr__", "__class__"}:
            if hasattr(self, "_disabled") and object.__getattribute__(self, "_disabled"):
                raise RuntimeError("Local subflow does not exist")
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevents setting subflow attributes after it is disabled."""
        if name != "_disabled":
            if hasattr(self, "_disabled") and object.__getattribute__(self, "_disabled"):
                raise RuntimeError("Local subflow does not exist")
        object.__setattr__(self, name, value)

    def add_entry_node(self, label: str = None) -> EntryNode:
        """Adds an entry node to the subflow.

        Args:
            label (str, optional): Label for the entry node. Defaults to None.

        Returns:
            EntryNode: EntryNode object added to the subflow.
        """
        entry_node = EntryNode(self._dag, label=label)
        self._dag.add_node(entry_node)
        return entry_node

    def add_exit_node(self, label: str = None) -> ExitNode:
        """Adds an exit node to the subflow.

        Args:
            label (str, optional): Label for the exit node. Defaults to None.

        Returns:
            ExitNode: ExitNode object added to the subflow.
        """
        exit_node = ExitNode(self._dag, label=label)
        self._dag.add_node(exit_node)
        return exit_node

    def add_local_parameter(
        self, parameter_type: str, name: str, value: str | int = "", description: str = ""
    ) -> "Subflow":
        """Adds a local parameter to the subflow. Default value is optional."""
        parameter_type = parameter_type.lower()
        if parameter_type in _ALLOWED_PARAM_TYPES_FOR_SUBFLOW:
            if parameter_type == "integer":
                new_param = Parameter(
                    name=name,
                    description=description,
                    prompt="",
                    value="",
                    valid_values=None,
                    type="int64",
                )
            else:
                new_param = Parameter(
                    name=name,
                    description=description,
                    prompt="",
                    value="",
                    type=parameter_type,
                    valid_values=None,
                )
            self.local_parameters.append(new_param)
            self._local_parameter_values[name] = str(value)
            return self
        else:
            raise ValueError(
                f"Unsupported param type: {parameter_type}. Supported types are: {_ALLOWED_PARAM_TYPES_FOR_SUBFLOW}"
            )

    def use_parameter_set(self, parameter_set: ParameterSet) -> "Subflow":
        """Use parameter set in the subflow."""
        for paramset in self.parameter_sets:
            if paramset.name == parameter_set.name:
                raise ValueError(f"Parameter set with name {parameter_set.name} is already in use in this subflow")
        self.parameter_sets.append(parameter_set)
        return self

    def set_local_parameter(self, name: str, value: str) -> "Subflow":
        """Set the value of a local parameter."""
        self._local_parameter_values[name] = value
        return self


class Subflows(CollectionModel):
    """Collection of Subflow objects."""

    def __init__(self, project: "Project") -> None:
        """Initialize the Subflows collection.

        Args:
            project: The Project object.
        """
        super().__init__()
        self._project = project
        self.unique_id = "asset_id"

    def _paginate(self, **kwargs: dict) -> Iterator[Subflow]:
        results = self._get_results_from_api(request_params=kwargs)
        for item in results.results["subflows"]:
            yield Subflow(project=self._project, **item)

    def _request_parameters(self) -> list:
        """Defines the accepted request parameters for subflows."""
        return [
            "asset_id",
            "project_id",
            "catalog_id",
            "space_id",
            "sort",
            "start",
            "limit",
            "entity.name",
            "entity.description",
        ]

    def __len__(self) -> int:
        """Returns the total number of subflows in the project."""
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        res = self._project._platform._batch_flow_api.list_batch_subflows(**query_params)
        res_json = res.json()
        return res_json["total_count"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Fetches subflow results from the API."""
        if "start" in request_params:
            parsed_url = urlparse(request_params["start"]["href"])
            params = parse_qs(parsed_url.query)
            request_params["start"] = params.get("start", [None])[0]

        request_params_defaults = {
            "data_intg_subflow_id": None,
            "project_id": self._project.metadata.guid,
            "catalog_id": None,
            "space_id": None,
            "sort": None,
            "start": None,
            "limit": 100,
            "entity.name": None,
            "entity.description": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        if "name" in request_params_unioned:
            request_params_unioned["entity_name"] = request_params_unioned.get("name")
        if "description" in request_params_unioned:
            request_params_unioned["entity_description"] = request_params_unioned.get("description")

        if "subflow_id" in request_params:
            response_json = self._project._platform._batch_flow_api.get_batch_subflows(
                **{k: v for k, v in request_params_unioned.items() if v is not None},
                data_intg_subflow_id=request_params["subflow_id"],
            ).json()
            response = {"data_flows": [response_json]}
        else:
            response = self._project._platform._batch_flow_api.list_batch_subflows(
                **{k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        subflows = []
        # Normalize and enrich each subflow object
        for subflow_json in response["data_flows"]:
            if subflow_json["metadata"]["asset_type"] == "data_intg_subflow":
                subflow_json["asset_id"] = subflow_json["metadata"]["asset_id"]
                subflow_json["name"] = subflow_json["metadata"]["name"]
                subflow_json["description"] = subflow_json["metadata"].get("description", None)
                subflows.append(subflow_json)
        response["subflows"] = subflows

        return CollectionModelResults(
            results=response,
            class_type=Subflow,
            response_bookmark="next",
            request_bookmark="start",
            response_location="subflows",
            constructor_params={"project": self._project},
        )
