# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains processors used by Python Generator."""

from ibm_watsonx_data_integration.codegen.code import Coder
from ibm_watsonx_data_integration.codegen.sources import ConnectionObjectSource, FlowObjectSource, Source


def processor_factory(source: Source, **kwargs: dict) -> Coder:
    """Factory wrapping source to appropriate Coder.

    Args:
        source: Source to generate code for
        **kwargs: additional key word arguments to pass into the processor object

    Raises:
        TypeError: if source is not a supported as a processor

    Returns:
        Coder: processor object
    """
    from ibm_watsonx_data_integration.codegen.processors.connection_processor import ConnectionProcessor
    from ibm_watsonx_data_integration.codegen.processors.streaming_processor import StreamingProcessor

    match source:
        case FlowObjectSource():
            return StreamingProcessor(source_data=source.to_json(), **kwargs)
        case ConnectionObjectSource():
            return ConnectionProcessor(source_data=source.to_json(), **kwargs)
        case _:
            raise TypeError(f"{type(source)} is currently not supported as a processor.")


__all__ = ["processor_factory"]
