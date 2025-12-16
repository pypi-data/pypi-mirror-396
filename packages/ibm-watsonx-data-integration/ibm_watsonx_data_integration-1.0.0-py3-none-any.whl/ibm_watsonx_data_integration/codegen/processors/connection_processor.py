#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Python Generator processor for connections."""

import json
from ibm_watsonx_data_integration.codegen.code import Code, Coder
from ibm_watsonx_data_integration.codegen.preamble import ConnectionPreamble
from ibm_watsonx_data_integration.common.constants import (
    PROD_BASE_API_URL,
    PROD_BASE_URL,
)
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from pprint import pformat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import IAMAuthenticator


class ConnectionProcessor(Coder):
    """Processor for recreating script to create a connection."""

    def __init__(
        self,
        source_data: dict,
        auth: "IAMAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
        base_api_url: str = PROD_BASE_API_URL,
    ) -> None:
        """The __init__ of the StreamingProcessor class.

        Args:
            source_data: Connection definition as python dictionary.
            auth: Authenticator instance.
            base_url: URL to IBM Cloud.
            base_api_url: URL to API endpoints.
        """
        self._source_data = source_data
        self._auth = auth
        self._preamble = ConnectionPreamble(source_data=source_data, base_url=base_url, base_api_url=base_api_url)

    def connection_as_str(self) -> str:
        """Returns project.create_connection statement."""
        environment = Environment(loader=FileSystemLoader(Path(__file__).parent / ".." / "_templates"))
        environment.filters["format_dict"] = pformat
        template = environment.get_template("create_connection.py.jinja")

        entity: dict = self._source_data["entity"]
        properties_json = "\n    ".join(json.dumps(entity["properties"], indent=4).splitlines())

        return template.render(
            name=entity["name"],
            datasource_id=entity["datasource_type"],
            description=entity.get("description", None),
            properties=properties_json,
        )

    def to_code(self) -> Code:
        """Returns object holding generated python script."""
        content = "\n".join([f"{self._preamble}", self.connection_as_str()])
        return Code(content=content)
