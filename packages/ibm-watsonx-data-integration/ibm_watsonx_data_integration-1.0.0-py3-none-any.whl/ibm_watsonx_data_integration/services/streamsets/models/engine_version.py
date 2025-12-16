#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Engine Version Models."""

from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class StreamingEngineStage(BaseModel):
    """Simple Stage definition available in a StreamingEngineStageLib."""

    name: str = Field(repr=True)
    label: str = Field(repr=True)
    type: str = Field(repr=True)
    subtype: str = Field(repr=False)
    description: str = Field(repr=True)

    _expose = True


class StreamingEngineStageLib(BaseModel):
    """Stage lib available in an engine version."""

    stage_lib_id: str = Field(repr=True)
    label: str = Field(repr=True)
    image_location: str = Field(repr=False)
    stages: list[StreamingEngineStage] = Field(repr=False)

    _expose = True


class StreamingEngineVersion(BaseModel):
    """Represents data for an engine version available on platform."""

    engine_version_id: str = Field(repr=True)
    image_tag: str = Field(repr=False)
    engine_type: str = Field(repr=True)
    stage_libs: list[StreamingEngineStageLib] | None = Field(default=None, repr=False)
    disabled: bool = Field(default=True, repr=True)
    release: bool = Field(default=False, repr=True)
    tunneling_supported: bool = Field(default=False, repr=True)

    _expose = True


class StreamingEngineVersions(CollectionModel):
    """Collection of streaming engine versions."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ for StreamingEngineVersions.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "engine_version_id"

    def __len__(self) -> int:
        """The total number of Streaming Engine Versions available."""
        return self._platform._environment_api.get_engine_versions(params={"include_stagelibs": False}).json()[
            "total_count"
        ]

    def _request_parameters(self) -> list:
        return ["engine_version_id", "include_stagelibs", "releases", "disabled"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: any) -> CollectionModelResults:
        """Returns all streaming engine versions based on params."""
        request_params_defaults = {
            "engine_version_id": None,
            "include_stagelibs": True,
            "releases": True,
            "disabled": None,
        }
        request_params_defaults.update(request_params)

        if request_params_defaults.get(self.unique_id) is not None:
            response = self._platform._environment_api.get_engine_by_version(
                engine_version=request_params_defaults[self.unique_id]
            )
            with open("single.json", "w") as f:
                import json

                f.write(json.dumps(response.json()))
            results = {"streamsets_engine_versions": [response.json()]}
        else:
            response = self._platform._environment_api.get_engine_versions(
                params={k: v for k, v in request_params_defaults.items() if v is not None}
            )
            results = response.json()

        return CollectionModelResults(
            results=results,
            class_type=StreamingEngineVersion,
            response_bookmark="next",
            request_bookmark="start",
            response_location="streamsets_engine_versions",
            constructor_params={},
        )
