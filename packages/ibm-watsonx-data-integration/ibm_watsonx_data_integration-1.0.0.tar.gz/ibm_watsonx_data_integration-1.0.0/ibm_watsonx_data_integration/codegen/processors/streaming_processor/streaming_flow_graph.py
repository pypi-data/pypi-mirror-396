#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module contains graph utility structures used for build streaming flow DAG."""

from collections import defaultdict
from collections.abc import Generator, Iterable
from ibm_watsonx_data_integration.services.streamsets.models.flow_model import PipelineDefinition
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.codegen.processors.streaming_processor.streaming_processor import (
        DefaultStageDefinition,
    )


class StageVertex:
    """Wrapper class for streaming flow stage."""

    def __init__(
        self,
        instance_name: str,
        stage_data: dict,
        default_stage_definition: "DefaultStageDefinition",
        number_suffix: int | None = None,
        output_lane_index: int = 0,
    ) -> None:
        """The __init__ of the StageVertex class.

        Args:
            instance_name: Uniq value used to determine stage.
            stage_data: Raw stage data taken from pipeline definition.
            default_stage_definition: Default stage definition configuration.
            number_suffix: Number of stage in whole pipeline definition.
            output_lane_index: Index indicating output lane index if stage has more than one.
        """
        self._instance_name = instance_name
        self._stage_data = stage_data
        self._default_stage_definition = default_stage_definition
        self._number_suffix = number_suffix
        self._output_lane_index = output_lane_index

        self.configuration: list[dict[str, Any]] = stage_data["configuration"]

    def __str__(self) -> str:
        """String representation of code to create stage."""
        stage_definition = (
            f'{self.stage_variable_name} = flow.add_stage("{self._default_stage_definition.label}", '
            f'type="{self.map_stage_type_to_human_readable(self._default_stage_definition.type)}")'
        )
        return f"{stage_definition}\n{self.stage_configuration()}".strip()

    @staticmethod
    def map_stage_type_to_human_readable(stage_type: str) -> str:
        """Map stage type from library definitions to value used by user.

        Reverse version of PipelineDefinition._NODE_TYPE dict.
        """
        stage_type_map = {"SOURCE": "origin", "TARGET": "destination", "EXECUTOR": "executor", "PROCESSOR": "processor"}
        return stage_type_map[stage_type]

    def __repr__(self) -> str:
        """Value used by repr function."""
        return self.instance_name

    def __hash__(self) -> int:
        """Hash value used in dict key search."""
        return hash(self.instance_name)

    def __eq__(self, other: object) -> bool:
        """Equal comparison logic."""
        if not isinstance(other, StageVertex):
            return False
        return self.instance_name == other.instance_name

    @property
    def instance_name(self) -> str:
        """Returns stage instance name from flow source JSON."""
        return self._instance_name

    @property
    def stage_variable_name(self) -> str:
        """Return variable name which will refer to stage in generated script."""
        stage_variable_name = self._default_stage_definition.label.lower().replace(" ", "_")
        if self._number_suffix:
            stage_variable_name = f"{stage_variable_name}_{self._number_suffix}"

        return stage_variable_name

    @property
    def output_lane_index(self) -> int:
        """Returns output lane index."""
        return self._output_lane_index

    def stage_configuration(self) -> str:
        """Return stage configuration properties changed by user."""
        changed_config_values = []
        for stage_config in self.configuration:
            if not stage_config.get("value"):
                continue

            value = stage_config.get("value")
            name = stage_config.get("name")
            config_definition = self._get_stage_config_definition(config_name=name)

            if value == config_definition["defaultValue"]:
                continue

            human_readable_config_name, _ = PipelineDefinition.get_attribute(config_definition)
            # For stage with predicates human-readable config name is `condition` but we need to use `predicates`.
            if name.lower() == "lanepredicates":
                human_readable_config_name = "predicates"
                value = self.process_lane_predicates_value(value)

            # TODO: WSDK-487
            processed_value = value
            if config_definition.get("type", "").lower() == "model":
                model_type = config_definition.get("model", {}).get("modelType", "")

                if model_type.lower() == "value_chooser":
                    processed_value = f'"{value}"'

            if config_definition.get("type", "").lower() in ("text", "string"):
                processed_value = f'"{value}"'

            if config_definition.get("mode", "").lower() == "text/x-sql":
                processed_value = f'"""{value}"""'

            if config_definition.get("type", "").lower() == "credential":
                processed_value = '"***"'

            changed_config_values.append(f"{self.stage_variable_name}.{human_readable_config_name} = {processed_value}")

        return "\n".join(changed_config_values)

    @staticmethod
    def process_lane_predicates_value(predicates: list[dict[str, str | int]]) -> list[dict]:
        """Utility function to remove `readonly_numbered_column_index` key from predicate dict.

        Args:
            predicates: List with predicates from flow definition.

        Returns:
            Processed list with predicates without `readonly_numbered_column_index` key.
        """
        for predicate in predicates:
            _ = predicate.pop("readonly_numbered_column_index", None)

        return predicates

    def _get_stage_config_definition(self, config_name: str) -> dict[str, Any]:
        for config in self._default_stage_definition.config_definitions:
            if config["name"] == config_name:
                return config

    def has_multiple_output_lanes(self) -> bool:
        """Returns if stage has multiple output lanes."""
        return len(self._stage_data["outputLanes"]) > 1


class Lane:
    """Represents lane between two stages in pipeline."""

    def __init__(self, source: StageVertex, dest: StageVertex, data: dict) -> None:
        """The __init__ method for Lane class.

        Args:
            source: Lane source vertex.
            dest: Lane destination vertex.
            data: Additional data assigned to lane.
        """
        self._source = source
        self._dest = dest
        self._data = data

    def __str__(self) -> str:
        """Returns string representation of lane."""
        if self._source.has_multiple_output_lanes():
            return (
                f"{self._source.stage_variable_name}.connect_output_to({self._dest.stage_variable_name}, "
                f"predicate={self._source.stage_variable_name}.predicates[{self._source.output_lane_index}])"
            )
        elif self._data.get("is_event_lane", False):
            return (
                f"{self._source.stage_variable_name}.connect_output_to({self._dest.stage_variable_name}, "
                f"event_lane=True)"
            )
        else:
            return f"{self._source.stage_variable_name}.connect_output_to({self._dest.stage_variable_name})"

    def __repr__(self) -> str:
        """Returns string representation of lane for repr function."""
        return f"{repr(self._source)} -> {repr(self._dest)}"


class StreamingFlowGraph:
    """Facade for building streaming flow DAG based on adjacent list."""

    def __init__(self) -> None:
        """The __init__ method of StreamingFlowGraph class."""
        self._adj_list: dict[StageVertex, list[Lane]] = defaultdict(list)

    @property
    def stage_vertexes(self) -> Iterable[StageVertex]:
        """Returns all graph stage vertexes."""
        return self._adj_list.keys()

    @property
    def lanes(self) -> Generator[Lane, None, None]:
        """Returns all graph lanes."""
        for _, lanes in self._adj_list.items():
            for lane in lanes:
                yield lane

    def add_stage_vertex(self, vertex: StageVertex) -> None:
        """Add new stage vertex to graph.

        Args:
            vertex: New vertex to add to graph structure.
        """
        _ = self._adj_list[vertex]

    def add_lane(self, source: StageVertex, dest: StageVertex, data: dict | None = None) -> None:
        """Add new lane from source to dest vertex.

        Args:
            source: Lane source vertex.
            dest: Lane destination vertex.
            data: Additional data that can be assigned to lane.
        """
        edge = Lane(source=source, dest=dest, data=data)
        self._adj_list[source].append(edge)

    def is_empty(self) -> bool:
        """Returns True when graph doesn't have any vertex."""
        return len(self._adj_list) == 0
