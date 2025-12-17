"""Helper classes to execute Aptly API calls."""

import configparser
import json
from typing import Any, BinaryIO, Dict, Optional, Union

import certifi
import requests

from cyberfusion.Common.Config import CyberfusionConfig


class AptlyApiCallException(Exception):
    """API call failed."""

    def __init__(self, body: Any, status_code: int) -> None:
        """Set attributes."""
        self.body = body
        self.status_code = status_code


class AptlyApiRequest:
    """Prepare API request and call AptlyApiCall."""

    SECTION_CONFIG = "aptly-api"

    KEY_CONFIG_SERVERURL = "serverurl"
    KEY_CONFIG_USERNAME = "username"
    KEY_CONFIG_APIKEY = "apikey"

    METHOD_GET = "GET"
    METHOD_PUT = "PUT"
    METHOD_POST = "POST"
    METHOD_DELETE = "DELETE"

    def __init__(self, config_file_path: Optional[str] = None) -> None:
        """Construct API request."""
        self.config = CyberfusionConfig(path=config_file_path)
        self.serverurl = self.config.get(self.SECTION_CONFIG, self.KEY_CONFIG_SERVERURL)

        # Set default values of nullable variables for type annotations

        self.data: Optional[Union[dict, str]] = None
        self.files: Optional[Dict[str, BinaryIO]] = None
        self.content_type_header: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None

        self.set_credentials()

    def set_credentials(self) -> None:
        """Set credentials in config."""
        try:
            self.username = self.config.get(
                self.SECTION_CONFIG, self.KEY_CONFIG_USERNAME
            )
        except configparser.NoOptionError:
            self.username = None

        try:
            self.password = self.config.get(self.SECTION_CONFIG, self.KEY_CONFIG_APIKEY)
        except configparser.NoOptionError:
            self.password = None

    def GET(self, path: str, data: Optional[dict] = None) -> None:
        """Set API GET request."""
        self.method = self.METHOD_GET
        self.path = path
        self.content_type_header = None  # Use default

    def PUT(self, path: str, data: dict) -> None:
        """Set API PUT request."""
        self.method = self.METHOD_PUT
        self.path = path
        self.data = json.dumps(data)
        self.content_type_header = AptlyApiCall.CONTENT_TYPE_JSON

    def POST(
        self,
        path: str,
        data: dict,
        files: Optional[Dict[str, BinaryIO]] = None,
    ) -> None:
        """Set API POST request.

        Either data or files may be specified.
        """
        self.method = self.METHOD_POST
        self.path = path
        self.files = files

        if self.data:
            self.data = json.dumps(data)
            self.content_type_header = AptlyApiCall.CONTENT_TYPE_JSON
        elif self.files:
            self.data = data
            self.content_type_header = None  # Use default

    def DELETE(self, path: str) -> None:
        """Set API DELETE request."""
        self.method = self.METHOD_DELETE
        self.path = path
        self.data = None
        self.content_type_header = None  # Use default

    def execute(self) -> dict:
        """Handle API request with AptlyApiCall."""
        cc = AptlyApiCall(
            method=self.method,
            serverurl=self.serverurl,
            path=self.path,
            username=self.username,
            password=self.password,
            content_type_header=self.content_type_header,
            data=self.data,
            files=self.files,
        )

        cc.execute()
        cc.check()

        return cc.response


class AptlyApiCall:
    """Construct, execute and check API call."""

    METHOD_GET = "GET"
    METHOD_PUT = "PUT"
    METHOD_POST = "POST"
    METHOD_DELETE = "DELETE"

    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_NAME_HEADER = "content-type"

    HTTP_CODE_BAD_REQUEST = 400

    NAME_HEADER_AUTHORIZATION = "Authorization"

    TIMEOUT_REQUEST = 60

    def __init__(
        self,
        method: str,
        serverurl: str,
        path: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        content_type_header: Optional[str] = None,
        data: Optional[Union[dict, str]] = None,
        files: Optional[Dict[str, BinaryIO]] = None,
    ) -> None:
        """Set API request attributes."""
        self.method = method
        self.serverurl = serverurl
        self.path = path
        self.username = username
        self.password = password
        self.content_type_header = content_type_header
        self.data = data
        self.files = files

    def construct(self) -> None:
        """Construct API request."""
        self.construct_url()
        self.construct_header()

    def construct_url(self) -> None:
        """Construct request URL."""
        self.url = "".join([self.serverurl, self.path])

    def construct_header(self) -> None:
        """Construct request headers."""
        self.headers = {}

        if self.content_type_header:
            self.headers[self.CONTENT_TYPE_NAME_HEADER] = self.content_type_header

    def execute(self) -> None:
        """Execute API request."""
        self.construct()

        if self.method == self.METHOD_GET:
            self.request = requests.get(
                self.url,
                headers=self.headers,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
                auth=(self.username, self.password),  # type: ignore[arg-type]
            )
        elif self.method == self.METHOD_PUT:
            self.request = requests.put(
                self.url,
                headers=self.headers,
                data=self.data,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
                auth=(self.username, self.password),  # type: ignore[arg-type]
            )
        elif self.method == self.METHOD_POST:
            self.request = requests.post(
                self.url,
                headers=self.headers,
                data=self.data,
                files=self.files,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
                auth=(self.username, self.password),  # type: ignore[arg-type]
            )
        elif self.method == self.METHOD_DELETE:
            self.request = requests.delete(
                self.url,
                headers=self.headers,
                verify=certifi.where(),
                timeout=self.TIMEOUT_REQUEST,
                auth=(self.username, self.password),  # type: ignore[arg-type]
            )

    def check(self) -> None:
        """Check API request status code and content type."""
        if self.request.status_code < self.HTTP_CODE_BAD_REQUEST:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                self.response = self.request.json()
            else:
                self.response = self.request.text
        else:
            if self.request.headers[self.CONTENT_TYPE_NAME_HEADER].startswith(
                self.CONTENT_TYPE_JSON
            ):
                raise AptlyApiCallException(
                    self.request.json(), self.request.status_code
                )
            else:
                raise AptlyApiCallException(self.request.text, self.request.status_code)
