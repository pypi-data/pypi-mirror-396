# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateErrorAnalysisRequest,
    CreateErrorAnalysisResponse,
)


def create_error_analysis_run_benchmarks__benchmark_uid__error_analysis_post(
    benchmark_uid: int,
    *,
    body: CreateErrorAnalysisRequest,
) -> CreateErrorAnalysisResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/error-analysis",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateErrorAnalysisResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateErrorAnalysisResponse
        response_201 = CreateErrorAnalysisResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_error_analysis_run_error_analysis__error_analysis_run_id__delete(
    error_analysis_run_id: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/error-analysis/{error_analysis_run_id}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import Cluster


@overload
def get_error_analysis_clusters_benchmarks__benchmark_uid__error_analysis__error_analysis_run_id__clusters_get(
    benchmark_uid: int, error_analysis_run_id: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_error_analysis_clusters_benchmarks__benchmark_uid__error_analysis__error_analysis_run_id__clusters_get(
    benchmark_uid: int, error_analysis_run_id: int, raw: Literal[False] = False
) -> Union[List["Cluster"], Any]: ...


def get_error_analysis_clusters_benchmarks__benchmark_uid__error_analysis__error_analysis_run_id__clusters_get(
    benchmark_uid: int, error_analysis_run_id: int, raw: bool = False
) -> Union[List["Cluster"], Any] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/error-analysis/{error_analysis_run_id}/clusters",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Union[List["Cluster"], Any]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Cluster']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Cluster.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ErrorAnalysisRun


@overload
def get_error_analysis_run_error_analysis__error_analysis_run_id__get(
    error_analysis_run_id: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_error_analysis_run_error_analysis__error_analysis_run_id__get(
    error_analysis_run_id: int, raw: Literal[False] = False
) -> ErrorAnalysisRun: ...


def get_error_analysis_run_error_analysis__error_analysis_run_id__get(
    error_analysis_run_id: int, raw: bool = False
) -> ErrorAnalysisRun | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/error-analysis/{error_analysis_run_id}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ErrorAnalysisRun:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ErrorAnalysisRun
        response_200 = ErrorAnalysisRun.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import LatestErrorAnalysisRunResponse
from ..types import UNSET


@overload
def get_latest_error_analysis_run_benchmarks__benchmark_uid__error_analysis_latest_run_get(
    benchmark_uid: int, *, prompt_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_latest_error_analysis_run_benchmarks__benchmark_uid__error_analysis_latest_run_get(
    benchmark_uid: int, *, prompt_execution_uid: int, raw: Literal[False] = False
) -> LatestErrorAnalysisRunResponse: ...


def get_latest_error_analysis_run_benchmarks__benchmark_uid__error_analysis_latest_run_get(
    benchmark_uid: int, *, prompt_execution_uid: int, raw: bool = False
) -> LatestErrorAnalysisRunResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["prompt_execution_uid"] = prompt_execution_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/error-analysis/latest-run",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> LatestErrorAnalysisRunResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as LatestErrorAnalysisRunResponse
        response_200 = LatestErrorAnalysisRunResponse.from_dict(response)

        return response_200

    return _parse_response(response)
