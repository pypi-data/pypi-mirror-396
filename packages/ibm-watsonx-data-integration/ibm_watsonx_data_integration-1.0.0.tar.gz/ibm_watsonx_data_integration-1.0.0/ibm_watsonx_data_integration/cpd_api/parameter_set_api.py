# (C) Copyright IBM Corp. 2025.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# IBM OpenAPI SDK Code Generator Version: 3.100.0-2ad7a784-20250212-162551

"""The IBM Parameter Sets service provides APIs to manage parameter sets.

API Version: 2.0.0
"""

import json
import requests
from ibm_watsonx_data_integration.common.auth import BaseAuthenticator
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import Any
from urllib.parse import quote

##############################################################################
# Service
##############################################################################


class ParameterSetApiClient(BaseAPIClient):
    """The parameter-set API service."""

    DEFAULT_SERVICE_URL = "https://dataplatform.dev.cloud.ibm.com/"
    DEFAULT_SERVICE_NAME = "parameter_set"
    disable_ssl = False

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
        disable_ssl_verification: bool = False,
    ) -> None:
        """Construct a new client for the parameter-set service.

        Args:
            auth: The Authentication object.
            base_url: The Parameter Set URL.
            disable_ssl_verification: Disable SSL verifcation.
        """
        super().__init__(auth=auth, base_url=base_url)

        self.disable_ssl = disable_ssl_verification

    def send_request(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | str | None = None,
        verify: bool | str = disable_ssl,
    ) -> requests.Response:
        """Sends a request with the given method, URL, headers, and other info and returns the resulting response.

        The purpose of this indirect method is to simplify the conversion to responses in the current base API client
        from responses in the old client.

        Args:
            method: The HTTP method of the request ex. GET, POST, etc.
            path: The origin + pathname according to WHATWG spec. In other words, the API call pathname.
            params: HTTP request parameters.
            data: HTTP request payload.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            An HTTP response from making the call.
        """
        full_url = _strip_extra_slashes(str(self.base_url) + path)
        return self._request(method=method, url=full_url, params=params, data=data, headers=headers, verify=verify)

    #########################
    # parameterSets
    #########################

    def get_parameter_sets(
        self,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        sort: str | None = None,
        start: str | None = None,
        limit: int | None = None,
        entity_name: str | None = None,
        entity_description: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """List parameter sets.

        Lists the parameter sets that are contained in the specified project or catalog
        (either project_id or catalog_id must be set). Only the metadata and a limited
        number of attributes from the entity of each data flow is returned.
        Use the following parameters to filter the results:
        | Field                    | Match type   | Example
         |
        | ------------------------ | ------------ |
        --------------------------------------- |
        | entity.name              | Equals       | ?entity.name=MyDataFlow
         |
        | entity.name              | Starts with  | ?entity.name=starts:MyDat
         |
        | entity.description          | Equals       | ?entity.description=profiling
               |
        | entity.description          | Starts with   |
        ?entity.description=starts:profiling           |
        To sort the returned results, use one or more of the parameters described in the
        following section. If no sort key is specified, the results are sorted in
        descending order on metadata.create_time, returning the most  recently created
        data flows first.
        | Field                     | Example                             |
        | ------------------------- | ----------------------------------- |
        | entity.name               | ?sort=+entity.name                  |
        | metadata.create_time      | ?sort=-metadata.create_time         |
        Multiple sort keys can be specified by delimiting them with a comma. For example,
        to sort in descending order on create_time and then in ascending order on name
        use: `?sort=-metadata.create_time,+entity.name`.definition.

        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param str sort: (optional) The field to sort the results on, including
               whether to sort ascending (+) or descending (-), for example,
               sort=-metadata.create_time.
        :param str start: (optional) The page token indicating where to start
               paging from.
        :param int limit: (optional) The limit of the number of items to return,
               for example limit=50. If not specified a default of 100 will be  used.
        :param str entity_name: (optional) Filter results based on the specified
               name.
        :param str entity_description: (optional) Filter results based on the
               specified description.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response with `dict` result representing a `ParameterSetPagedCollection` object
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "sort": sort,
            "start": start,
            "limit": limit,
            "entity.name": entity_name,
            "entity.description": entity_description,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = "/v2/parameter_sets"
        response = self.send_request(method="GET", path=url, headers=headers, params=params, verify=True)
        return response

    def create_parameter_set(
        self,
        *,
        parameter_set: dict[str, Any] = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        asset_category: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """Create parameter set.

        Creates a parameter set in the specified project or catalog (either project_id or
        catalog_id must be set). All subsequent calls to use the parameter set must
        specify the project or catalog ID the parameter set was created in.

        :param ParameterSetObject parameter_set: (optional) Object holding the
               parameters array.
        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param str asset_category: (optional) The category of the asset. Must be
               either SYSTEM or USER. Only a registered service can use this parameter.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response with `dict` result representing a `ParameterSet` object
        """
        # if parameter_set is not None:
        #     parameter_set = _convert_model(parameter_set)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "asset_category": asset_category,
        }

        data = {
            "parameter_set": parameter_set,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json;charset=utf-8"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = "/v2/parameter_sets"

        response = self.send_request(method="POST", path=url, headers=headers, params=params, data=data, verify=True)
        return response

    def delete_parameter_sets(
        self,
        id: list[str],
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """Delete parameter sets.

        Delete the specified parameter sets from a project or catalog (either project_id
        or catalog_id must be set).

        :param List[str] id: The list of parameter set IDs to delete.
        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response
        """
        if id is None:
            raise ValueError("id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "id": ",".join(id),
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]

        url = "/v2/parameter_sets"
        response = self.send_request(method="DELETE", path=url, headers=headers, params=params, verify=True)
        return response

    def get_parameter_set(
        self,
        parameter_set_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """Get parameter set.

        Get details of a specific parameter set.

        :param str parameter_set_id: The parameter set ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response with `dict` result representing a `ParameterSet` object
        """
        if not parameter_set_id:
            raise ValueError("parameter_set_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = f"/v2/parameter_sets/{quote(parameter_set_id, safe='')}"
        response = self.send_request(method="GET", path=url, headers=headers, params=params, verify=True)
        return response

    def patch_parameter_set(
        self,
        parameter_set_id: str,
        parameter_set_patch_entity: dict[str, Any],
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """Patch a parameter set.

        Patch a parameter set in the specified project or catalog (either project_id or
        catalog_id must be set).

        :param str parameter_set_id: The parameter set ID to use.
        :param List[PatchDocument] parameter_set_patch_entity: The patch operations
               to apply.
        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response with `dict` result representing a `ParameterSet` object
        """
        if not parameter_set_id:
            raise ValueError("parameter_set_id must be provided")
        if parameter_set_patch_entity is None:
            raise ValueError("parameter_set_patch_entity must be provided")

        # print(parameter_set_patch_entity)
        # parameter_set_patch_entity = [_convert_model(x) for x in parameter_set_patch_entity]
        # print(parameter_set_patch_entity)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = json.dumps(parameter_set_patch_entity)

        headers["content-type"] = "application/json;charset=utf-8"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = f"/v2/parameter_sets/{quote(parameter_set_id, safe='')}"
        response = self.send_request(method="PATCH", path=url, headers=headers, params=params, data=data, verify=True)

        return response

    def clone_parameter_set(
        self,
        parameter_set_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> requests.Response:
        """Clone parameter set.

        Clone a parameter set.

        :param str parameter_set_id: The parameter set ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use. catalog_id,
               space_id, or project_id is required.
        :param str project_id: (optional) The ID of the project to use. catalog_id,
               space_id, or project_id is required.
        :param str space_id: (optional) The ID of the space to use. catalog_id,
               space_id, or project_id is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `requests.Response` containing the result, headers and HTTP status code.
        :rtype: requests.Response with `dict` result representing a `ParameterSet` object
        """
        if not parameter_set_id:
            raise ValueError("parameter_set_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = f"/v2/parameter_sets/{quote(parameter_set_id, safe='')}/clone"
        response = self.send_request(method="POST", path=url, headers=headers, params=params, verify=True)
        return response


def _strip_extra_slashes(value: str) -> str:
    """Combine multiple trailing slashes to a single slash."""
    if value.endswith("//"):
        return value.rstrip("/") + "/"
    return value


# Helper function
@staticmethod
def _encode_path_vars(*args: str) -> list[str]:
    """Encode path variables to be substituted into a URL path.

    Arguments:
        args: A list of strings to be URL path encoded

    Returns:
        A list of encoded strings that are safe to substitute into a URL path.
    """
    return (requests.utils.quote(x, safe="") for x in args)
