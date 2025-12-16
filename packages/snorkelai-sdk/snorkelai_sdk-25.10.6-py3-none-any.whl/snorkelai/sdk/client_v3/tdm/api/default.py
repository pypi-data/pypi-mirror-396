# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


@overload
def get_documentation_docs_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_documentation_docs_get(raw: Literal[False] = False) -> Any: ...


def get_documentation_docs_get(raw: bool = False) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/docs",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal


@overload
def get_open_api_endpoint_api_v1_openapi_json_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_open_api_endpoint_api_v1_openapi_json_get(
    raw: Literal[False] = False,
) -> Any: ...


def get_open_api_endpoint_api_v1_openapi_json_get(
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/api/v1/openapi.json",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, cast, overload

import requests
from typing_extensions import Literal


@overload
def get_version_version_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_version_version_get(raw: Literal[False] = False) -> str: ...


def get_version_version_get(raw: bool = False) -> str | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/version",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> str:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as str
        # Direct parsing for str
        return cast(str, response)

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def home__get(
    *, timeout_secs: Union[Unset, int] = 300, raw: Literal[True]
) -> requests.Response: ...


@overload
def home__get(
    *, timeout_secs: Union[Unset, int] = 300, raw: Literal[False] = False
) -> Any: ...


def home__get(
    *, timeout_secs: Union[Unset, int] = 300, raw: bool = False
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["timeout_secs"] = timeout_secs

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
