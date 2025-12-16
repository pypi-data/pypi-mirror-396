"""Module for batch flow."""

# from ..components.local_message_handler import LocalMessageHandler
# from ..components.message_handler import MessageHandler
# from ibm.datastage._framework.paramsets import LocalParameters, ParameterSet
# from ibm.datastage._framework.runtime import Runtime
# from ibm.datastage._framework.schema.data_definition import DataDefinition
import copy
import json
import requests
from collections import defaultdict
from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow, PayloadExtender
from ibm_watsonx_data_integration.cpd_models.parameter_set_model import (
    _ALLOWED_PARAM_TYPES,
    Parameter,
    ParameterSet,
)
from pydantic import Field
from typing import TYPE_CHECKING, Any
from typing_extensions import override
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project

import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.extractor import FlowExtractor

# from ibm_watsonx_data_integration.services.datastage._console import console
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import DAG, Link, Node, SuperNode, SuperNodeRef
from ibm_watsonx_data_integration.services.datastage.models.flow_stages import FlowComposer

# from ibm_watsonx_data_integration.services.datastage.models.flow_runner import FlowRunner
from ibm_watsonx_data_integration.services.datastage.models.layout import LayeredLayout
from ibm_watsonx_data_integration.services.streamsets.models.environment_model import Environment


class BatchFlowConfiguration(BaseModel):
    """Configuration for a BatchFlow."""

    environment: str = None
    warn_limit: int | None = None
    retention_days: int | None = None
    retention_amount: int | None = None
    _project: "Project" = None

    def as_dict(self) -> dict:
        """Return dict version of configuration for job._create call."""
        new_job = {"configuration": dict()}
        if self.environment:
            new_job["configuration"]["env_id"] = self.environment + "-" + self._project.project_id

        if self.warn_limit:
            new_job["configuration"]["flow_limits"] = {"warn_limit": self.warn_limit}

        if self.retention_days and self.retention_amount:
            raise ValueError("Flow cannot have both retention_days and retention_amount")
        if self.retention_days:
            new_job["retention_policy"] = {"days": self.retention_days}
        elif self.retention_amount:
            new_job["retention_policy"] = {"amount": self.retention_amount}

        return new_job


class CompileMode(Enum):
    """Defines the execution run mode for the DataStage flow."""

    ETL = "ETL"
    TETL = "TETL"
    ELT = "ELT"


class ELTMaterializationPolicy(Enum):
    """Defines the SQL pushdown (ELT) optimization strategy."""

    NESTED_QUERY = ("Generate nested SQL", "NESTED_QUERY")
    INTERMEDIATE_TABLE = ("Link as table", "INTERMEDIATE_TABLE")
    INTERMEDIATE_VIEW = ("Link as view", "INTERMEDIATE_VIEW")
    MATERIALIZE_CARDINALITY_CHANGERS = ("Advanced", "MATERIALIZE_CARDINALITY_CHANGERS")

    def __init__(self, label: str, enum_value: str) -> None:
        """Initializes the ELTMaterializationPolicy enum member."""
        self.label = label
        self.enum_value = enum_value

    def to_dict(self) -> dict:
        """Returns the dictionary representation for the JSON payload."""
        data = {"label": self.label, "value": self.enum_value}
        # The 'id' field only exists for NESTED_QUERY
        if self == ELTMaterializationPolicy.NESTED_QUERY:
            data["id"] = "nesting"
        return data


@Flow.register("batch")
class BatchFlow(FlowComposer, Flow):
    """Represents a batch flow."""

    rcp: bool = False
    acp: bool = True
    _project: "Project" = None
    name: str = "unnamed_flow"
    description: str = ""
    # env : Environment = None
    flow_id: str = ""
    parameter_sets: list[ParameterSet] = []
    local_parameters: list[Parameter] = []
    value_set_selected: dict[str, str] = {}
    job_parameters: list[dict[str, Any]] = []  # noqa: ANN401
    configuration: "BatchFlowConfiguration" = Field(BatchFlowConfiguration(), exclude=True)
    runMode: str = CompileMode.ETL.value
    ELTDropdown: dict = None

    def __init__(self, project: "Project" = None, dag: "DAG" = None, **kwargs: Any) -> None:  # noqa: ANN401, D417
        """Initialize a batch flow.

        Args:
           project: The project for the flow to be created in. If None, then the flow is not created remotely.
           name: The flow name.
           description: The flow description.
           dag: Optional dag to copy.
           flow_type: The type of flow. This should always be datastage.
        """
        Flow.__init__(self, **kwargs)
        if dag:
            FlowComposer.__init__(self, copy.deepcopy(dag))  # could change to a custom DAG copy method in the future
        else:
            FlowComposer.__init__(self, DAG())
        self._project = project
        self.configuration._project = project
        self._compile_mode: CompileMode = CompileMode.ETL
        self._elt_materialization_policy: ELTMaterializationPolicy | None = None

        # Initialize Pydantic fields from property backing values
        self.runMode = self._compile_mode.value
        self.ELTDropdown = ELTMaterializationPolicy.NESTED_QUERY.to_dict()

    # def use_data_definition(self, data_definition: DataDefinition):
    #     self.data_definitions.append(data_definition)
    #     return self

    # def use_message_handler(self, message_handler: MessageHandler):
    #     self.message_handlers.append(message_handler)
    #     return self

    # def use_local_message_handler(self, local_message_handler: LocalMessageHandler):
    #     self.local_message_handler = local_message_handler
    #     return self

    def use_parameter_set(self, parameter_set: ParameterSet) -> "BatchFlow":
        """Use parameter set in flow."""
        if parameter_set.name == "PROJDEF":
            for parameter in parameter_set.parameters:
                parameter.value = "PROJDEF"
                self.local_parameters.append(parameter)
            return self
        else:
            for paramset in self.parameter_sets:
                if paramset.name == parameter_set.name:
                    raise ValueError(f"Parameter set with name {parameter_set.name} is already in use in this flow")
            self.parameter_sets.append(parameter_set)
            return self

    def use_projdef_parameter(self, parameter: Parameter) -> "BatchFlow":
        """Use a PROJDEF parameter in flow."""
        parameter.value = "PROJDEF"
        self.local_parameters.append(parameter)
        return self

    def add_local_parameter(
        self,
        parameter_type: str,
        name: str,
        description: str = "",
        prompt: str = "",
        value: Any = "",  # noqa: ANN401
        valid_values: list[Any] | None = [],  # noqa: ANN401
    ) -> "BatchFlow":
        """Add a local parameter to flow."""
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
            self.local_parameters.append(new_param)
            return self
        else:
            raise ValueError(f"Unsupported param type: {parameter_type}. Supported types are: {_ALLOWED_PARAM_TYPES}")

    def set_runtime_value_set(self, parameter_set_name: str, value_set_name: str) -> "BatchFlow":
        """Set the value set of a parameter set for this flow."""
        for parameter_set in self.parameter_sets:
            if parameter_set.name == parameter_set_name:
                for value_set in parameter_set.value_sets:
                    if value_set.name == value_set_name:
                        self.value_set_selected[parameter_set_name] = value_set_name
                        return self
                raise ValueError(f"Parameter set {parameter_set_name} has no value set {value_set_name}")
        raise ValueError(f"This flow has no parameter set {parameter_set_name}")

    def set_runtime_parameter_value(self, parameter_set_name: str, parameter_name: str, value: Any) -> "BatchFlow":  # noqa: ANN401
        """Set the value of a runtime parameter in a parameter set for this flow to use during all job runs."""
        for parameter_set in self.parameter_sets:
            if parameter_set.name == parameter_set_name:
                for parameter in parameter_set.parameters:
                    if parameter.name == parameter_name:
                        self.job_parameters.append({"name": f"{parameter_set_name}.{parameter_name}", "value": value})
                        return self
                raise ValueError(f"Parameter set {parameter_set_name} has no parameter {parameter_name}")
        raise ValueError(f"This flow has no parameter set {parameter_set_name}")

    def set_runtime_local_parameter(self, local_parameter_name: str, value: Any) -> "BatchFlow":  # noqa: ANN401
        """Set the value of a runtime local parameter for this flow to use during all job runs."""
        for local_param in self.local_parameters:
            if local_param.name == local_parameter_name:
                self.job_parameters.append({"name": local_parameter_name, "value": value})
                return self
        raise ValueError(f"This flow has no local parameter {local_parameter_name}")

    # def use_localparams(self, localparams: LocalParameters):
    #     self.local_parameters = localparams
    #     return self

    # def use_runtime(self, runtime: Runtime):
    #     self.runtime = runtime
    #     return self

    def use_runtime_column_propagation(self, rcp: bool = True) -> "BatchFlow":
        """Enable rcp."""
        self.rcp = rcp
        return self

    def use_auto_column_propagation(self, acp: bool = True) -> "BatchFlow":
        """Enable acp."""
        self.acp = acp
        return self

    # def _add_ghost_node(self) -> Node:
    #     node = GhostNode(self._dag)
    #     self._dag.add_node(node)
    #     return node

    # def add_markdown_comment(self, text: str) -> MarkdownComment:
    #     comment = MarkdownComment(self._dag, content=text)
    #     self._dag.add_node(comment)
    #     return comment

    # def add_styled_comment(self, text: str) -> StyledComment:
    #     comment = StyledComment(self._dag, content=text)
    #     self._dag.add_node(comment)
    #     return comment

    def get_link(self, source: Node, destination: Node) -> Link:
        """Gets the link between two nodes in the flow. If there are no links or multiple links, it raises an error.

        Args:
            source: Node from which the link originates.
            destination: Node to which the link points.

        Returns:
            The single link between the source and destination nodes.
        """
        links = self._dag.get_links_between(source, destination)
        if len(links) == 0:
            raise ValueError("No link between nodes")
        if len(links) > 1:
            raise ValueError("Multiple links between nodes")
        return links[0]

    def get_links(self, source: Node, destination: Node) -> list[Link]:
        """Gets all links between two nodes in the flow.

        Args:
            source: Node from which the links originate.
            destination: Node to which the links point.

        Returns:
            A list of Links between the source and destination nodes.
        """
        return self._dag.get_links_between(source, destination)

    @staticmethod
    def _blank_json(description: str) -> dict:
        return {
            "primary_pipeline": "",
            "pipelines": [
                {
                    "nodes": [],
                    "description": description,
                    "id": "",
                    "app_data": {"datastage": {}, "ui_data": {"comments": []}},
                    "runtime_ref": "",
                }
            ],
            "json_schema": "http://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json",
            "schemas": [],
            "doc_type": "pipeline",
            "id": "",
            "app_data": {
                "datastage": {},
                "additionalProperties": {
                    "transInputLinkMapper": {},
                    "ELTDropdown": ELTMaterializationPolicy.NESTED_QUERY.to_dict(),
                    "disableParamsCacheOnFlow": False,
                    "rcpLinkList": [],
                    "globalAcp": True,
                    "enableRCP": False,
                    "isNewTransActive": False,
                    "enableSchemaLessDesign": False,
                    "runMode": CompileMode.ETL.value,
                },
            },
            "version": "3.0",
        }

    def _dag_to_json(self) -> str:
        def _compute_local_supernode_metadata(node: SuperNode) -> None:
            node._dag.compute_metadata()
            sub_lay = LayeredLayout(node._dag)
            sub_lay.compute()

            for sub_node in node._dag.nodes():
                if isinstance(sub_node, SuperNode) and sub_node.is_local:
                    _compute_local_supernode_metadata(sub_node)

        if not self._dag.adj:
            return json.dumps(BatchFlow._blank_json(self.description))

        self._dag.compute_metadata()
        lay = LayeredLayout(self._dag)
        lay.compute()

        # Compute layout for child DAGs for local subflows
        for node in self._dag.nodes():
            if isinstance(node, SuperNode):
                if node.is_local:
                    _compute_local_supernode_metadata(node)
                # else:
                #     for paramset in node.parameter_sets:
                #         node._parent_fc.use_parameter_set(paramset)

        ser = FlowExtractor(self)
        ser.extract()

        flow_model = ser.serialize()
        return flow_model.model_dump_json(indent=2, exclude_none=True, by_alias=True, warnings=False)

    @staticmethod
    def _create(
        project: "Project" = None,
        name: str = "unnamed_flow",
        environment: Environment = None,
        description: str = "",
        flow_type: str = "batch",
    ) -> "BatchFlow":
        # self.parameter_sets: list[ParameterSet] = []
        # self.local_parameters: LocalParameters | None = None
        # self.runtime: Runtime | None = None
        # self.message_handlers: list[MessageHandler] = []
        # self.local_message_handler: LocalMessageHandler | None = None
        # self.data_definitions: list[DataDefinition] = []

        flow_name = name

        project_id = project.metadata.guid

        response = project._platform._batch_flow_api.create_batch_flows(
            data_intg_flow_name=flow_name,
            pipeline_flows=BatchFlow._blank_json(description),
            project_id=project_id,
        )

        flow = BatchFlow(
            project=project,
            name=name,
            description=description,
            flow_type=flow_type,
            flow_id=response.json()["metadata"]["asset_id"],
        )
        return flow

    @staticmethod
    def create_or_get(
        project: "Project" = None,
        name: str = "unnamed_flow",
        environment: Environment = None,
        description: str = "",
        flow_type: str = "batch",
    ) -> "BatchFlow":
        """Either creates the flow with the given name or returns the preexisting flow of that name."""
        try:
            return project.batch_flows.get(name=name)
        except ValueError:
            return BatchFlow._create(project, name, environment, description, flow_type)

    def _update(self) -> requests.Response:
        flow_name = self.name
        flow_json = json.loads(self._dag_to_json())
        project_id = self._project.metadata.guid
        response = self._project._platform._batch_flow_api.update_batch_flows(
            data_intg_flow_id=self.flow_id,
            data_intg_flow_name=flow_name,
            pipeline_flows=flow_json,
            project_id=project_id,
            parameter_sets=self.parameter_sets,
            local_parameters=self.local_parameters,
        )

        # Manually update description, will try to combine these two api calls later
        if response.json()["metadata"]["description"] != self.description:
            response = self._project._platform._datastage_flow_api.patch_attributes_datastage_flow(
                data_intg_flow_id=self.flow_id, project_id=project_id, description=self.description
            )
        return response

    def _delete(self) -> requests.Response:
        return self._project._platform._batch_flow_api.delete_batch_flows(
            id=[self.flow_id],
            project_id=self._project.metadata.guid,
        )

    def compile(self) -> requests.Response:
        """Compile a flow and return the response."""
        flow_json = self._dag_to_json()
        project_id = self._project.metadata.guid
        compile_params = {}

        if self._compile_mode == CompileMode.ELT:
            compile_params["enable_sql_pushdown"] = True
        elif self._compile_mode == CompileMode.TETL:
            compile_params["enable_pushdown_source"] = True

        response = self._project._platform._batch_flow_api.compile_batch_flows(
            data_intg_flow_id=self.flow_id, pipeline_flows=flow_json, project_id=project_id, **compile_params
        )
        return response

    def _duplicate(self, name: str, description: str) -> "BatchFlow":
        project_id = self._project.metadata.guid

        response = self._project._platform._batch_flow_api.clone_batch_flows(
            data_intg_flow_id=self.flow_id, project_id=project_id, data_intg_flow_name=name
        )
        flow = BatchFlow(
            project=self._project,
            name=name,
            description=description,
            flow_type="batch",
            flow_id=response.json()["metadata"]["asset_id"],
            dag=self._dag,
            parameter_sets=self.parameter_sets,
            local_parameters=self.local_parameters,
        )
        # set the description
        # flow._update()
        return flow

    def get_compile_status(self, **kwargs: dict) -> requests.Response:
        """Get status for compiling a flow."""
        project_id = self._project.metadata.guid
        response = self._project._platform._batch_flow_api.get_flow_compile_status(
            data_intg_flow_id=self.flow_id, project_id=project_id, **kwargs
        )
        return response

    def get_compile_info(self, **kwargs: dict) -> requests.Response:
        """Get response for compiling a flow."""
        project_id = self._project.metadata.guid
        response = self._project._platform._batch_flow_api.batch_flows_compile_info(
            data_intg_flow_id=self.flow_id, project_id=project_id, **kwargs
        )
        return response

    def _get_parameter_sets_list(self) -> list:
        """Get parameter set list for job._create call."""
        parameter_sets = []
        for paramset in self.parameter_sets:
            param_name = paramset.name
            if param_name in self.value_set_selected:
                parameter_sets.append(
                    {
                        "name": param_name,
                        "ref": paramset.parameter_set_id,
                        "value_set": self.value_set_selected[param_name],
                    }
                )
            else:
                parameter_sets.append({"name": param_name, "ref": paramset.parameter_set_id})
        return parameter_sets

    @property
    def compile_mode(self) -> CompileMode:
        """The compile mode for the BatchFlow (ETL/TETL/ELT)."""
        return self._compile_mode

    @compile_mode.setter
    def compile_mode(self, compile_mode: CompileMode) -> None:
        """Set the compile mode. When switching to ELT, apply the stored ELT option.

        Args:
            compile_mode: The new CompileMode to set.
        """
        if not isinstance(compile_mode, CompileMode):
            raise TypeError("compile_mode must be an instance of CompileMode")
        self._compile_mode = compile_mode
        self.runMode = compile_mode.value

    @property
    def elt_materialization_policy(self) -> "ELTMaterializationPolicy | None":
        """ELT materialization policy used when the flow's `compile_mode` is `CompileMode.ELT`.

        Returns the stored `ELTMaterializationPolicy` or ``None`` if not set.
        Setting this property is only allowed when ``compile_mode`` is
        ``CompileMode.ELT``; attempting to set it in any other compile
        mode raises a ``RuntimeError``.
        """
        return self._elt_materialization_policy

    @elt_materialization_policy.setter
    def elt_materialization_policy(self, option: "ELTMaterializationPolicy | None") -> None:
        """Set the ELT materialization policy.

        Args:
            option: The `ELTMaterializationPolicy` to set, or ``None`` to clear.

        Raises:
            RuntimeError: If the flow is not in `CompileMode.ELT`.
            TypeError: If `option` is not an `ELTMaterializationPolicy` or ``None``.
        """
        if option is not None and not isinstance(option, ELTMaterializationPolicy):
            raise TypeError("elt_materialization_policy must be an instance of ELTMaterializationPolicy or None")
        if self._compile_mode != CompileMode.ELT:
            raise RuntimeError("ELT materialization policy can only be set when compile_mode is CompileMode.ELT")
        self._elt_materialization_policy = option
        # Sync with Pydantic field
        if option is not None:
            self.ELTDropdown = option.to_dict()
        else:
            self.ELTDropdown = ELTMaterializationPolicy.NESTED_QUERY.to_dict()


class BatchFlows(CollectionModel):
    """Collection of BatchFlow objects."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the BatchFlows class.

        Args:
            project: The Project object.
        """
        super().__init__(project)
        self._project = project
        self.unique_id = "flow_id"

    def _request_parameters(self) -> list:
        return [
            "data_intg_flow_id",
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
        """The len of the BatchFlows class."""
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        res = self._project._platform._batch_flow_api.list_batch_flows(**query_params)
        res_json = res.json()
        return res_json["total_count"]

    def _replace_super_nodes(self, fc: Flow) -> None:
        replace_nodes: defaultdict[dict] = defaultdict(dict)

        def replace_super_node_refs(dtc: DAG) -> None:
            for node in dtc.nodes():
                if isinstance(node, SuperNodeRef):
                    super_node = self._project.subflows.get(subflow_id=node.subflow_id)
                    super_node._load_pipeline_id()
                    super_node.url = node.url
                    super_node.label = node.label
                    replace_nodes[dtc][node] = super_node
                    replace_super_node_refs(super_node._dag)
                if isinstance(node, SuperNode):
                    replace_super_node_refs(node._dag)

        replace_super_node_refs(fc._dag)

        for dag, node_dict in replace_nodes.items():
            for node, replacement in node_dict.items():
                dag.replace_node(node, replacement)

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "start" in request_params:
            parsed_url = urlparse(request_params["start"]["href"])
            params = parse_qs(parsed_url.query)
            request_params["start"] = params.get("start", [None])[0]

        request_params_defaults = {
            "data_intg_flow_id": None,
            "project_id": self._project.metadata.guid,
            "catalog_id": None,
            "space_id": None,
            "sort": None,
            "start": None,
            "limit": 100,
            "entity.name": None,
            "entity.description": None,
        }
        dag = None
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        if "entity.name" in request_params_unioned:
            request_params_unioned["entity_name"] = request_params_unioned.get("entity.name")
        if "entity.description" in request_params_unioned:
            request_params_unioned["entity_description"] = request_params_unioned.get("entity.description")

        if "flow_id" in request_params:
            response_json = self._project._platform._batch_flow_api.get_batch_flows(
                **{k: v for k, v in request_params_unioned.items() if v is not None},
                data_intg_flow_id=request_params["flow_id"],
            ).json()
            response = {"data_flows": [response_json]}
            flow_json = response_json
            flow_model = models.Flow(**flow_json["attachments"])
            from ibm_watsonx_data_integration.services.datastage.codegen.dag_generator import DAGGenerator

            dag_gen = DAGGenerator(flow_model)
            fc = dag_gen.generate()

            response_json |= fc.model_dump()
            parameter_sets = []
            external_paramsets = flow_json["attachments"].get("external_paramsets", [])
            for parameter_set in external_paramsets:
                paramset = self._project.parameter_sets.get(parameter_set_id=parameter_set["ref"])
                dump = paramset.model_dump()
                dump["_project"] = self._project
                parameter_sets.append(dump)
            response_json["parameter_sets"] = parameter_sets

            self._replace_super_nodes(fc)

            dag = fc._dag

        else:
            response = self._project._platform._batch_flow_api.list_batch_flows(
                **{k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        # Create parameters for construction
        for flow_json in response["data_flows"]:
            flow_json["flow_id"] = flow_json["metadata"]["asset_id"]
            flow_json["name"] = flow_json["metadata"]["name"]
            if "description" in flow_json["metadata"]:
                flow_json["description"] = flow_json["metadata"]["description"]

        return CollectionModelResults(
            results=response,
            class_type=BatchFlow,
            response_bookmark="next",
            request_bookmark="start",
            response_location="data_flows",
            constructor_params={"project": self._project, "dag": dag},
        )


class BatchFlowPayloadExtender(PayloadExtender):
    """Batch flow extender setup also compiles the flow.

    :meta: private
    """

    @override
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        if not flow.get_compile_info().json()["metadata"]["compiled"]:
            flow.compile()
        payload["asset_ref"] = flow.flow_id
        return payload
