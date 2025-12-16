# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains common sources for PythonGenerator."""

from ibm_watsonx_data_integration.codegen.sources.base_source import Source
from ibm_watsonx_data_integration.codegen.sources.connection_object_source import ConnectionObjectSource
from ibm_watsonx_data_integration.codegen.sources.flow_object_source import FlowObjectSource
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.codegen.generator import Generatable


def source_factory(source: "Generatable") -> Source:
    """Factory wrapping source to appropriate object.

    Args:
        source: Input source that contains flow definition.

    Raises:
        TypeError: If input source type is not supported.
    """
    from ibm_watsonx_data_integration.cpd_models.connections_model import Connection
    from ibm_watsonx_data_integration.cpd_models.flow_model import Flow

    match source:
        case Flow():
            return FlowObjectSource(source)
        case Connection():
            return ConnectionObjectSource(source)
        case _:
            raise TypeError(f"{type(source)} is currently not supported as a source.")


__all__ = ["source_factory"]
