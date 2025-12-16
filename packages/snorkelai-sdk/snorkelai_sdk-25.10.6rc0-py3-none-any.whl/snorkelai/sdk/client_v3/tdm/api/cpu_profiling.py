# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CPUProfilingParams, CPUProfilingStatusResponse


def clear_profiling_cpu_profile_clear_post(
    *,
    body: CPUProfilingParams,
) -> CPUProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/cpu-profile/clear",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CPUProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CPUProfilingStatusResponse
        response_200 = CPUProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    ProfileCpuProfileGetResponseProfileCpuProfileGet,
)
from ..types import UNSET, Unset


@overload
def profile_cpu_profile_get(
    *, service: str, output_as_tree: Union[Unset, bool] = False, raw: Literal[True]
) -> requests.Response: ...


@overload
def profile_cpu_profile_get(
    *,
    service: str,
    output_as_tree: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> ProfileCpuProfileGetResponseProfileCpuProfileGet: ...


def profile_cpu_profile_get(
    *, service: str, output_as_tree: Union[Unset, bool] = False, raw: bool = False
) -> ProfileCpuProfileGetResponseProfileCpuProfileGet | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["service"] = service

    params["output_as_tree"] = output_as_tree

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/cpu-profile",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ProfileCpuProfileGetResponseProfileCpuProfileGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ProfileCpuProfileGetResponseProfileCpuProfileGet
        response_200 = ProfileCpuProfileGetResponseProfileCpuProfileGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from ..models import CPUProfilingParams, CPUProfilingStatusResponse


def start_profiling_cpu_profile_start_post(
    *,
    body: CPUProfilingParams,
) -> CPUProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/cpu-profile/start",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CPUProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CPUProfilingStatusResponse
        response_200 = CPUProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import CPUProfilingParams, CPUProfilingStatusResponse


def stop_profiling_cpu_profile_stop_post(
    *,
    body: CPUProfilingParams,
) -> CPUProfilingStatusResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/cpu-profile/stop",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CPUProfilingStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CPUProfilingStatusResponse
        response_200 = CPUProfilingStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)
