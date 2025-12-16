#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing utils."""

import logging
import yaml
from functools import wraps
from requests.exceptions import HTTPError
from time import sleep, time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.models import BaseModel

logger = logging.getLogger()


def matches_filters(obj: "BaseModel", **kwargs: dict) -> bool:
    """Returns True if the object's attributes match the provided key-value filters.

    Args:
        obj: The object to inspect.
        **kwargs: Keyword arguments representing attribute names and their
                  expected values.

    Returns:
        True if all attributes on the object match the values in kwargs.

    Raises:
        ValueError: If a filter key does not exist as an attribute on the object.
    """
    for key in kwargs:
        if not hasattr(obj, key):
            raise ValueError(f"Cannot filter on {key}")
    return all(getattr(obj, key) == kwargs[key] for key in kwargs)


class SeekableList(list):
    """A list where we return objects based on the matches_filters method."""

    def get(self, **kwargs: dict) -> "BaseModel":
        """Retrieve the first instance that matches the supplied arguments.

        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            The first instance from the group that matches the supplied arguments.
        """
        try:
            return next(i for i in self if matches_filters(i, **kwargs))
        except StopIteration:
            raise ValueError("Instance ({}) is not in list".format(", ".join(f"{k}={v}" for k, v in kwargs.items())))

    def get_all(self, **kwargs: dict) -> "SeekableList[BaseModel]":
        """Retrieve all instances that match the supplied arguments.

        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`ibm_watsonx_data_integration.common.utils.SeekableList` of results
            that match the supplied arguments.
        """
        return SeekableList(i for i in self if matches_filters(i, **kwargs))


class TraversableDict(dict):
    """A dictionary where they key can be a string used to navigate multiple levels."""

    def __init__(self, data: dict, string_key_splitter: str = ".") -> None:
        """ """  # noqa: D419
        super().__init__(data)
        self.string_key_splitter = string_key_splitter

    def __setitem__(self, key_path: str, value: Any) -> None:  # noqa: ANN401
        """ """  # noqa: D419
        keys = key_path.split(self.string_key_splitter)
        if len(keys) <= 1:
            return super().__setitem__(keys[0], value)

        tmp_data = super().__getitem__(keys[0])
        # Traverse to the key depth
        for key in keys[1:-1]:
            if isinstance(tmp_data, list):
                key = int(key)

            tmp_data = tmp_data[key]
        return tmp_data.__setitem__(keys[-1], value)

    def __getitem__(self, key_path: str) -> Any:  # noqa: ANN401
        """ """  # noqa: D419
        # Returns Value given key path
        keys = key_path.split(self.string_key_splitter)
        tmp_data = super().__getitem__(keys[0])
        # Traverse to the key depth
        for key in keys[1:]:
            if isinstance(tmp_data, list):
                key = int(key)

            tmp_data = tmp_data[key]
        return tmp_data

    def __delitem__(self, key_path: str) -> None:
        """ """  # noqa: D419
        keys = key_path.split(self.string_key_splitter)
        if len(keys) <= 1:
            return super().__delitem__(keys[0])

        tmp_data = super().__getitem__(keys[0])
        # Traverse to the key depth
        for key in keys[1:-1]:
            if isinstance(tmp_data, list):
                key = int(key)

            tmp_data = tmp_data[key]
        del tmp_data[keys[-1]]

    def __contains__(self, key_path: str) -> bool:
        """ """  # noqa: D419
        keys = key_path.split(self.string_key_splitter)
        if len(keys) <= 1:
            return super().__contains__(keys[0])
        tmp_data = super().__getitem__(keys[0])
        # Traverse to the key depth
        for key in keys[1:-1]:
            if key in tmp_data:
                if isinstance(tmp_data, list):
                    key = int(key)

                tmp_data = tmp_data[key]
            else:
                return False
        return keys[-1] in tmp_data


def wait_and_retry_on_http_error(timeout_sec: int = 10, time_between_calls_sec: int = 2) -> any:
    """Decorator to retry a function on HTTPError for draft runs and snapshots using tunneling.

    Retries the decorated function upon encountering an HTTPError, logging a warning and waiting
    between attempts until the specified timeout is reached.

    Args:
        func: The function to decorate.
        timeout_sec: Maximum time to keep retrying (default is 300 seconds).
        time_between_calls_sec: Wait time between retry attempts (default is 2 seconds).
    """

    def decorator(func: callable) -> any:
        @wraps(func)
        def inner(*args: any, **kwargs: any) -> any:
            end_time = time() + timeout_sec
            error = None
            while time() < end_time:
                try:
                    return func(*args, **kwargs)
                except HTTPError as e:
                    error = e
                    logger.warning(
                        "HTTPError occurred. Retrying in a bit.",
                        extra=dict(error=e, wait_time_for_next_call=time_between_calls_sec),
                    )
                    sleep(time_between_calls_sec)
            raise error

        return inner

    return decorator


def get_params_from_swagger(content_string: str, request_path: str) -> list:
    """Extract the request params from file.

    Args:
        content_string: The full swagger defintion in string format.
        request_path: The path of the request you want the parameters from.

    Returns:
        A list of request parameters.
    """
    request_params = []
    data = TraversableDict(yaml.safe_load(content_string), "%")
    param_locations = data["paths"][request_path]["get"]["parameters"]
    for param_location in param_locations:
        param_location = param_location["$ref"]
        param_location = param_location.replace("#/", "").replace("/", "%")
        request_params.append(data[param_location]["name"].replace("entity.", "").replace("metadata.", ""))
    return request_params


def _require_env(expected_on_prem: bool) -> any:
    """Internal decorator factory enforcing on_prem/saas mode."""

    def decorator(func: any) -> any:
        @wraps(func)
        def wrapper(self: any, *args: any, **kwargs: any) -> any:
            # Check if we are in a Platform object
            if not hasattr(self, "on_prem"):
                platform = getattr(self, "_platform", None)
                if platform is None:
                    raise AttributeError(f"{self.__class__.__name__} missing '_platform' attribute.")
                actual = getattr(platform, "on_prem", None)
            else:
                actual = getattr(self, "on_prem", None)

            # Validate
            if actual != expected_on_prem:
                env_type = "on-prem" if expected_on_prem else "SaaS"
                raise RuntimeError(
                    f"This function is only available for {env_type} "
                    f"(current environment: {'on-prem' if actual else 'SaaS'})."
                )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def on_prem_only(func: any) -> any:
    """Decorator enforcing platform.on_prem == True."""
    return _require_env(True)(func)


def saas_only(func: any) -> any:
    """Decorator enforcing platform.on_prem == False."""
    return _require_env(False)(func)
