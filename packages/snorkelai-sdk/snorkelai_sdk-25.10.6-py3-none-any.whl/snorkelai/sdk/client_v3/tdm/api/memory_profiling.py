# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    MemoryProfilingParams,
    MemoryProfilingStatusResponse,
)


def clear_profiling_memory_profile_clear_post(
    *,
    body: MemoryProfilingParams,
) -> MemoryProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/memory-profile/clear",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> MemoryProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as MemoryProfilingStatusResponse
        response_200 = MemoryProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Union, cast, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def get_tracemalloc_profile_tracemalloc_get(
    *, top_k: Union[Unset, int] = 5, depth: Union[Unset, int] = 5, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_tracemalloc_profile_tracemalloc_get(
    *,
    top_k: Union[Unset, int] = 5,
    depth: Union[Unset, int] = 5,
    raw: Literal[False] = False,
) -> str: ...


def get_tracemalloc_profile_tracemalloc_get(
    *, top_k: Union[Unset, int] = 5, depth: Union[Unset, int] = 5, raw: bool = False
) -> str | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["top_k"] = top_k

    params["depth"] = depth

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/tracemalloc",
        "params": params,
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


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import MemoryProfilingTraceResponse, PersistenceMode
from ..types import Unset


@overload
def memory_profile_memory_profile_get(
    *,
    service: str,
    pid: Union[Unset, str] = UNSET,
    persistence_mode: Union[Unset, PersistenceMode] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def memory_profile_memory_profile_get(
    *,
    service: str,
    pid: Union[Unset, str] = UNSET,
    persistence_mode: Union[Unset, PersistenceMode] = UNSET,
    raw: Literal[False] = False,
) -> MemoryProfilingTraceResponse: ...


def memory_profile_memory_profile_get(
    *,
    service: str,
    pid: Union[Unset, str] = UNSET,
    persistence_mode: Union[Unset, PersistenceMode] = UNSET,
    raw: bool = False,
) -> MemoryProfilingTraceResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["service"] = service

    params["pid"] = pid

    json_persistence_mode: Union[Unset, str] = UNSET
    if not isinstance(persistence_mode, Unset):
        json_persistence_mode = persistence_mode.value

    params["persistence_mode"] = json_persistence_mode

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/memory-profile",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> MemoryProfilingTraceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as MemoryProfilingTraceResponse
        response_200 = MemoryProfilingTraceResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    MemoryProfilingParams,
    MemoryProfilingStatusResponse,
)


def start_profiling_memory_profile_start_post(
    *,
    body: MemoryProfilingParams,
) -> MemoryProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/memory-profile/start",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> MemoryProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as MemoryProfilingStatusResponse
        response_200 = MemoryProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import StartTraceMalloc


def start_tracemalloc_tracemalloc_start_post(
    *,
    body: StartTraceMalloc,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/tracemalloc/start",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import (
    MemoryProfilingParams,
    MemoryProfilingStatusResponse,
)


def stop_profiling_memory_profile_stop_post(
    *,
    body: MemoryProfilingParams,
) -> MemoryProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/memory-profile/stop",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> MemoryProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as MemoryProfilingStatusResponse
        response_200 = MemoryProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any


def stop_tracemalloc_tracemalloc_stop_post() -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/tracemalloc/stop",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
