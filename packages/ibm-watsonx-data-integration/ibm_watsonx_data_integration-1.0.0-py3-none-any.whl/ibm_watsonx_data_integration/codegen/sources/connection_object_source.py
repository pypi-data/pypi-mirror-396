#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Source class from Connection model."""

from ibm_watsonx_data_integration.codegen.sources.base_source import Source
from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.connections_model import Connection


class ConnectionObjectSource(Source):
    """Loads and converts to intermediate format connection definition from ``Connection`` object."""

    def __init__(self, connection: "Connection") -> None:
        """The __init__ of the ConnectionObjectSource class.

        Args:
            connection: Connection object instance.
        """
        self._connection = connection

    @override
    def to_json(self) -> dict:
        return self._connection.model_dump(exclude_unset=False)
