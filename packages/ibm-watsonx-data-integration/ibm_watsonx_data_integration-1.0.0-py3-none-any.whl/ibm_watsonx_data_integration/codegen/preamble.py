# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Contains classes responsible for generating python script preamble."""

import textwrap
from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.common.constants import (
    PROD_BASE_API_URL,
    PROD_BASE_URL,
)
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import ClassVar
from typing_extensions import override

TEMPLATE_DIR = Path(__file__).parent / "_templates"
TEMPLATE_LOADER = FileSystemLoader(TEMPLATE_DIR)
TEMPLATE_ENVIRONMENT = Environment(loader=TEMPLATE_LOADER)


class Preamble(ABC):
    """Script preamble containing required imports and class initialization."""

    def __init__(
        self,
        source_data: dict,
        base_url: str = PROD_BASE_URL,
        base_api_url: str = PROD_BASE_API_URL,
        api_key_env_var_name: str = "IBM_CLOUD_API_KEY",
    ) -> None:
        """The __init__ of the Preamble class.

        Args:
            source_data: Raw flow data.
            base_url: URL for IBM Cloud.
            base_api_url: URL for API endpoints.
            api_key_env_var_name: Environment variable which contains API Key.
        """
        self._source_data = source_data
        self._base_url = base_url
        self._base_api_url = base_api_url
        self._api_key_var_name = api_key_env_var_name

    @abstractmethod
    def __str__(self) -> str:
        """Here we should return preamble string representation."""


class StreamingPreamble(Preamble):
    """Preamble for streaming flow recreation scripts."""

    @override
    def __str__(self) -> str:
        return textwrap.dedent(f"""\
import os
from ibm_watsonx_data_integration import Platform
from ibm_watsonx_data_integration.common.auth import IAMAuthenticator


auth = IAMAuthenticator(
    api_key=os.getenv("{self._api_key_var_name}"),
    base_auth_url="{self._base_url}",
)
platform = Platform(
    auth=auth,
    base_url="{self._base_url}",
    base_api_url="{self._base_api_url}",
)

project = platform.projects.get(project_id="{self._source_data["flow"]["metadata"]["project_id"]}")
env = project.environments.get(environment_id="{self._source_data["flow"]["entity"]["streamsets_flow"]["environment_id"]}")
flow = project.create_flow(name="{self._source_data["flow"]["metadata"]["name"]}", environment=env, description="{self._source_data["flow"]["metadata"]["description"]}")
""")  # noqa: E501


class ConnectionPreamble(Preamble):
    """Preamble for connection recreation scripts."""

    _template: ClassVar[Template] = TEMPLATE_ENVIRONMENT.get_template("connection_preamble.py.jinja")

    @override
    def __str__(self) -> str:
        return self._template.render(
            api_key_var_name=self._api_key_var_name,
            base_url=self._base_url,
            base_api_url=self._base_api_url,
            project_id=self._source_data.get("metadata", {}).get("project_id", "<INSERT PROJECT ID>"),
        )
