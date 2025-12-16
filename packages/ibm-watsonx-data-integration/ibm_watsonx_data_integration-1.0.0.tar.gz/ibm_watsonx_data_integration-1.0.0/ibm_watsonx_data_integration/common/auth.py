# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Authentication module."""

import base64
import json
import logging
import requests
import time
from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.common.exceptions import (
    InvalidApiKeyError,
    InvalidUrlError,
)
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)


class BaseAuthenticator(ABC):
    """Base Authenticator classes to be inherited by other authenticators."""

    def __init__(self, disable_ssl_verification: bool = False) -> None:
        """Initializes BaseAuthenticator.

        Args:
            disable_ssl_verification: Whether to disable SSL Verification.

        """
        self.disable_ssl_verification = disable_ssl_verification

    @abstractmethod
    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            The value to be plugged into the `Authorization` header of a request.
        """
        pass


class IAMAuthenticator(BaseAuthenticator):
    """Authenticator class to authenticate using an IBM Cloud IBM API Key.

    Attributes:
        api_key: API key being used to authenticate.
        token_url: URL being used to authenticate against.
        iam_token: The token generated using the api_key and url.
        token_expiry_time: UNIX time in seconds for when the token will expire.
    """

    # give a time buffer for expiration, to have ample time to make a request without the token being expired.
    EXPIRATION_TIME_BUFFER = 5

    def __init__(
        self, api_key: str, base_auth_url: str = "https://cloud.ibm.com", disable_ssl_verification: bool = False
    ) -> None:
        """Initializes IAM Authenticator.

        Args:
            api_key: The API key to be used for authentication.
            base_auth_url: The base URL of the IBM cloud instance to be used for authentication.
            disable_ssl_verification: Whether to disable SSL Verification.

        Raises:
            InvalidApiKeyError: If api_key is not of type str, or is an empty str.
            InvalidUrlError: If base_auth_url is not of type str, or is an empty str.
            requests.exceptions.HTTPError: If there is an error getting a valid token.
        """
        super().__init__(disable_ssl_verification=disable_ssl_verification)
        if not isinstance(api_key, str):
            raise InvalidApiKeyError("api_key should be of type str.")
        if not api_key:
            raise InvalidApiKeyError("api_key should not be an empty str.")

        if not isinstance(base_auth_url, str):
            raise InvalidUrlError("base_auth_url should be of type str.")
        if not base_auth_url:
            raise InvalidUrlError("base_auth_url should not be an empty str.")

        self._base_auth_url = base_auth_url
        self.api_key = api_key

        # base_auth_url looks like: "https://cloud.ibm.com"
        # token url looks like: "https://iam.cloud.ibm.com/identity/token"
        parsed_url = urlparse(url=base_auth_url)
        new_netloc = "iam." + parsed_url.netloc
        new_path = parsed_url.path + "/identity/token"
        self.token_url = urlunparse((parsed_url.scheme, new_netloc, new_path, "", "", ""))

        self.iam_token = None
        self.token_expiry_time = None
        self.request_token()

    def request_token(self) -> None:
        """Request a token from the servers using the API key.

        Raises:
            InvalidApiKeyError: If api_key is invalid.
            InvalidUrlError: If token_url is invalid.
            requests.exceptions.HTTPError: If there is an error getting a valid token.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"apikey": self.api_key, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

        try:
            response = requests.post(self.token_url, headers=headers, data=data)
        except requests.exceptions.ConnectionError as e:
            logger.error("IAMAuthenticator incorrect URL. %s", e)
            raise InvalidUrlError("IAMAuthenticator incorrect URL.")
        if response.status_code == 400:
            raise InvalidApiKeyError("IAMAuthenticator api_key is not valid.")
        response.raise_for_status()

        self.iam_token = response.json()["access_token"]
        self.token_expiry_time = response.json()["expiration"]

    def get_token(self) -> str:
        """Get existing token, or request a new one if the current token is expired.

        Returns:
            The current bearer token used for auth.
        """
        current_time = int(time.time())
        if self.iam_token is None:
            logger.debug("Getting first token.")
            self.request_token()
        elif (current_time + self.EXPIRATION_TIME_BUFFER) >= self.token_expiry_time:
            logger.debug("Previous token expired, refreshing.")
            self.request_token()

        return self.iam_token

    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            The value to be plugged into the `Authorization` header of a request.
        """
        return f"Bearer {self.get_token()}"


class ZenApiKeyAuthenticator(BaseAuthenticator):
    """Authentication class for using a Zen API Key."""

    def __init__(self, username: str, zen_api_key: str, disable_ssl_verification: bool = False) -> None:
        """__init__ for the class.

        Args:
            username: Username to use for authentication.
            zen_api_key: Zen API Key to use for authentication.
            disable_ssl_verification: Whether to disable SSL Verification.
        """
        super().__init__(disable_ssl_verification=disable_ssl_verification)
        self.username = username
        self.zen_api_key = zen_api_key
        self.disable_ssl_verification = disable_ssl_verification

    def encode(self) -> str:
        """Encodes the username and Zen API key in base64.

        Returns:
            The base64-encoded string "<username>:<zen_api_key>".
        """
        combined = f"{self.username}:{self.zen_api_key}"
        encoded_bytes = base64.b64encode(combined.encode("utf-8"))

        return encoded_bytes.decode("utf-8")

    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            The value to be plugged into the `Authorization` header of a request.
        """
        return f"ZenApiKey {self.encode()}"


class BearerTokenAuthenticator(BaseAuthenticator):
    """Authentication class for directly using a bearer token."""

    def __init__(self, bearer_token: str, disable_ssl_verification: bool = False) -> None:
        """__init__ for the class.

        Args:
            bearer_token: bearer token to use for authentication.
            disable_ssl_verification: Whether to disable SSL Verification.
        """
        super().__init__(disable_ssl_verification)
        self.bearer_token = bearer_token
        self.disable_ssl_verification = disable_ssl_verification

    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            The value to be plugged into the `Authorization` header of a request.
        """
        return f"Bearer {self.bearer_token}"


class ICP4DAuthenticator(BaseAuthenticator):
    """Authenticator for on-prem cpd using IAM or API credentials."""

    AUTH_PATH = "/icp4d-api/v1/authorize"
    # give a time buffer for expiration, to have ample time to make a request without the token being expired.
    EXPIRATION_TIME_BUFFER = 5

    def __init__(
        self,
        url: str,
        username: str,
        password: str | None = None,
        zen_api_key: str | None = None,
        disable_ssl_verification: bool = False,
    ) -> None:
        """Init for ICP4D Authenticator.

        Args:
            url: CPD instance URL
            username: Username of the user trying to authenticate
            password: Password of the user, if provided zen_api_key should be left None
            zen_api_key: ZenApiKey of the user, if provided password should be left None
            disable_ssl_verification: Whether to disable SSL verification. Default: ``False``.
        """
        super().__init__(disable_ssl_verification=disable_ssl_verification)

        if not url.endswith(self.AUTH_PATH):
            url = url + self.AUTH_PATH

        self.url = url

        self.username = username

        if password and zen_api_key:
            raise ValueError("Both password and zen_api_key should not be supplied. Only one.")

        self.password = password
        self.zen_api_key = zen_api_key

        self.iam_bearer_token = None

    def request_token(self) -> None:
        """Requests a new token from the endpoint."""
        logger.debug("Requesting cp4d token.")
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url=self.url,
            headers=headers,
            data=json.dumps(dict(username=self.username, password=self.password, api_key=self.zen_api_key)),
            verify=not self.disable_ssl_verification,
        )
        response.raise_for_status()
        self.iam_bearer_token = response.json()["token"]

    def get_token(self) -> str:
        """Get existing token, or request a new one if the current token is expired.

        Returns:
            The current bearer token used for auth.
        """
        if self.iam_bearer_token is None:
            self.request_token()

        return self.iam_bearer_token

    def get_authorization_header(self) -> str:
        """Get the authorization header to be used for requests."""
        return f"Bearer {self.get_token()}"
