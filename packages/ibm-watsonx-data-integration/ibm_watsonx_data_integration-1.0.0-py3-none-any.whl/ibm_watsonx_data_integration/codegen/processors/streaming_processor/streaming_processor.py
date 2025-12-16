#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Python Generator processors for streaming flow."""

import copy
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from ibm_watsonx_data_integration.codegen.code import Code, Coder
from ibm_watsonx_data_integration.codegen.preamble import StreamingPreamble
from ibm_watsonx_data_integration.codegen.processors.streaming_processor.streaming_flow_graph import (
    StageVertex,
    StreamingFlowGraph,
)
from ibm_watsonx_data_integration.common.constants import (
    PROD_BASE_API_URL,
    PROD_BASE_URL,
)
from ibm_watsonx_data_integration.services.streamsets.api import EnvironmentApiClient
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import IAMAuthenticator


@dataclass(frozen=True)
class DefaultStageDefinition:
    """Wrapper structure for stage definition."""

    label: str
    type: str
    config_definitions: list[dict[str, Any]]


class StreamingProcessor(Coder):
    """Main processor for recreating script to create streaming flow.

    Responsible for creating ``StageVertex`` class for each stage within pipeline definition.
    Handle building relation graph between stages using adjacency list.
    """

    _definitions: dict[str, DefaultStageDefinition] | None

    def __init__(
        self,
        source_data: dict,
        auth: "IAMAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
        base_api_url: str = PROD_BASE_API_URL,
    ) -> None:
        """The __init__ of the StreamingProcessor class.

        Args:
            source_data: Streaming flow definition as python dictionary.
            auth: Authenticator instance.
            base_url: URL to IBM Cloud.
            base_api_url: URL to API endpoints.
        """
        self._source_data = source_data
        self._environment_api_client = EnvironmentApiClient(auth=auth, base_url=base_api_url)
        self._stage_counter = defaultdict(int)
        self._stages = list()
        self._preamble = StreamingPreamble(source_data=source_data, base_url=base_url, base_api_url=base_api_url)
        self._lanes_to_vertex_lookup = dict()
        self._graph = StreamingFlowGraph()
        self._definitions = None

    @property
    def definitions(self) -> dict[str, DefaultStageDefinition]:
        """Parsed stage definitions with configuration definition."""
        if not self._definitions:
            res_json = self._environment_api_client.get_library_definitions_for_engine_version(
                engine_version=self._source_data["flow"]["entity"]["streamsets_flow"]["engine_version"]
            ).json()
            self._definitions = self._parse_definition_response(res_json)

        return self._definitions

    @property
    def graph(self) -> StreamingFlowGraph:
        """Returns streaming flow DAG structure."""
        if self._graph.is_empty():
            self._extract_stages()

        return self._graph

    @staticmethod
    def _parse_definition_response(definition_json: dict) -> dict[str, DefaultStageDefinition]:
        result = dict()
        for _, stage_definition in definition_json["stageDefinitionMap"].items():
            stage_name = stage_definition["name"]
            result[stage_name] = DefaultStageDefinition(
                label=stage_definition["label"],
                type=stage_definition["type"],
                config_definitions=copy.deepcopy(stage_definition["configDefinitions"]),
            )

        return result

    def _extract_stages(self) -> None:
        """Actual StaveVertex creation and building relation graph between stages."""
        for stage_dict in self._source_data["pipeline_definition"]["stages"]:
            self._stage_counter[stage_dict["stageName"]] += 1
            default_stage_definition: DefaultStageDefinition = self.definitions[stage_dict["stageName"]]

            for index, output_lane_id in enumerate(stage_dict["outputLanes"]):
                vertex = StageVertex(
                    instance_name=stage_dict["instanceName"],
                    stage_data=stage_dict,
                    default_stage_definition=default_stage_definition,
                    number_suffix=self._stage_counter[stage_dict["stageName"]],
                    output_lane_index=index,
                )
                self._lanes_to_vertex_lookup[output_lane_id] = vertex

            for event_lane_id in stage_dict["eventLanes"]:
                vertex = StageVertex(
                    instance_name=stage_dict["instanceName"],
                    stage_data=stage_dict,
                    default_stage_definition=default_stage_definition,
                    number_suffix=self._stage_counter[stage_dict["stageName"]],
                )
                self._lanes_to_vertex_lookup[event_lane_id] = vertex

            for input_lane_id in stage_dict["inputLanes"]:
                is_event_lane = True if "eventlane" in input_lane_id.lower() else False

                vertex = StageVertex(
                    instance_name=stage_dict["instanceName"],
                    stage_data=stage_dict,
                    default_stage_definition=default_stage_definition,
                    number_suffix=self._stage_counter[stage_dict["stageName"]],
                )
                source = self._lanes_to_vertex_lookup[input_lane_id]

                # Code order dependency here: first lane then vertex
                self._graph.add_lane(source, vertex, {"is_event_lane": is_event_lane})
                self._graph.add_stage_vertex(vertex)

    def stages_as_str(self) -> str:
        """Collect string representation of all stages.

        Returns:
            A string representation of create stage code for all stages.
        """
        result = []
        for stage in self.graph.stage_vertexes:
            result.append(str(stage))

        return "\n".join(result)

    def stages_connection_as_str(self) -> str:
        """Collect string representation of connection between stages.

        Returns:
            A string representation of connection between stages.
        """
        result = []
        for lane in self.graph.lanes:
            result.append(str(lane))

        return "\n".join(result)

    @property
    def script_footer(self) -> str:
        """Return generated script footer."""
        return "project.update_flow(flow)"

    def to_code(self) -> Code:
        """Returns object holding generated python script."""
        content = textwrap.dedent(f"""\
{self._preamble}

{self.stages_as_str()}

{self.stages_connection_as_str()}

{self.script_footer}
""")
        return Code(content=content)
