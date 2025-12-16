# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Flows module."""

# Can't be part of flow_model.py due to circular imports
import itertools
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel
from ibm_watsonx_data_integration.common.utils import SeekableList
from ibm_watsonx_data_integration.services.datastage.models import (
    BatchFlows,
)
from ibm_watsonx_data_integration.services.streamsets.models import (
    StreamingFlows,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project


class Flows(CollectionModel):
    """Collection of BatchFlow and StreamingFlow objects."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the Flows class.

        Args:
            project: The Project object.
        """
        self._sx_flows = StreamingFlows(project)
        self._data_flows = BatchFlows(project)
        self._project = project

    def _paginate(self, **kwargs: dict) -> BaseModel:
        for item in itertools.chain(self._sx_flows, self._data_flows):
            yield item

    def __len__(self) -> int:
        """Total amount of flows."""
        params = {"project_id": self._project.project_id, "limit": 0}
        return self._project._platform._streaming_flow_api.get_streaming_flows(params=params).json().get("total_count")

    def get_all(self, flow_type: str = None, **kwargs: dict) -> SeekableList:
        """Used to get multiple (all) results from flows api.

        Args:
            flow_type: The type of flow to be returned
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :py:obj:`list` of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        if flow_type == "streaming":
            return self._sx_flows.get_all(**kwargs)
        elif flow_type == "batch":
            return self._data_flows.get_all(**kwargs)
        else:
            return self._sx_flows.get_all(**kwargs) + self._data_flows.get_all(**kwargs)

    def get(self, flow_type: str = None, **kwargs: dict) -> SeekableList:
        """Used to get an instant result from the api.

        Args:
            flow_type: The type of flow to be returned
            **kwargs: Optional arguments to be passed to filter the results.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.

        Raises:
            ValueError: If instance is not in the list.
        """
        if flow_type == "streaming":
            return self._sx_flows.get(**kwargs)
        elif flow_type == "batch":
            return self._data_flows.get(**kwargs)
        else:
            try:
                return self._sx_flows.get(**kwargs)
            except Exception:
                return self._data_flows.get(**kwargs)
