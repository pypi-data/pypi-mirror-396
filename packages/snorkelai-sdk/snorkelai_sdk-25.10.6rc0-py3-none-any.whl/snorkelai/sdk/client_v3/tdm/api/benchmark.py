# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import Benchmark, CreateBenchmarkPayload


def create_benchmark_benchmarks_post(
    *,
    body: CreateBenchmarkPayload,
) -> Benchmark:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Benchmark:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Benchmark
        response_201 = Benchmark.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import (
    BenchmarkExecution,
    CreateBenchmarkExecutionPayload,
)


def create_benchmark_execution_benchmarks__benchmark_uid__executions_post(
    benchmark_uid: int,
    *,
    body: CreateBenchmarkExecutionPayload,
) -> BenchmarkExecution:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/executions",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> BenchmarkExecution:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BenchmarkExecution
        response_202 = BenchmarkExecution.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import BenchmarkConfig


@overload
def export_benchmark_config_benchmarks__benchmark_uid__export_config_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def export_benchmark_config_benchmarks__benchmark_uid__export_config_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> BenchmarkConfig: ...


def export_benchmark_config_benchmarks__benchmark_uid__export_config_get(
    benchmark_uid: int, raw: bool = False
) -> BenchmarkConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/export/config",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BenchmarkConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BenchmarkConfig
        response_200 = BenchmarkConfig.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import Benchmark


@overload
def get_benchmark_benchmarks__benchmark_uid__get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_benchmark_benchmarks__benchmark_uid__get(
    benchmark_uid: int, raw: Literal[False] = False
) -> Benchmark: ...


def get_benchmark_benchmarks__benchmark_uid__get(
    benchmark_uid: int, raw: bool = False
) -> Benchmark | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Benchmark:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Benchmark
        response_200 = Benchmark.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import Benchmark
from ..types import UNSET, Unset


@overload
def get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get(
    *,
    workflow_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get(
    *,
    workflow_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["Benchmark"]: ...


def get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get(
    *,
    workflow_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    include_archived: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["Benchmark"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workflow_uid"] = workflow_uid

    params["workspace_uid"] = workspace_uid

    params["include_archived"] = include_archived

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Benchmark"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Benchmark']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Benchmark.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import Dataset


@overload
def get_linked_datasets_for_benchmark_benchmarks__benchmark_uid__datasets_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_linked_datasets_for_benchmark_benchmarks__benchmark_uid__datasets_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> List["Dataset"]: ...


def get_linked_datasets_for_benchmark_benchmarks__benchmark_uid__datasets_get(
    benchmark_uid: int, raw: bool = False
) -> List["Dataset"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/datasets",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Dataset"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Dataset']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Dataset.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet,
)


@overload
def get_metrics_by_benchmark_benchmarks__benchmark_uid__executions_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_metrics_by_benchmark_benchmarks__benchmark_uid__executions_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet: ...


def get_metrics_by_benchmark_benchmarks__benchmark_uid__executions_get(
    benchmark_uid: int, raw: bool = False
) -> (
    GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/executions",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet
        response_200 = GetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGetResponseGetMetricsByBenchmarkBenchmarksBenchmarkUidExecutionsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import BenchmarkFilterStructuresResponse


@overload
def get_populated_filters_info_benchmarks__benchmark_uid__populated_filters_info_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_populated_filters_info_benchmarks__benchmark_uid__populated_filters_info_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> BenchmarkFilterStructuresResponse: ...


def get_populated_filters_info_benchmarks__benchmark_uid__populated_filters_info_get(
    benchmark_uid: int, raw: bool = False
) -> BenchmarkFilterStructuresResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/populated-filters-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BenchmarkFilterStructuresResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BenchmarkFilterStructuresResponse
        response_200 = BenchmarkFilterStructuresResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import BenchmarkExecutionExportMetadata
from ..types import UNSET, Unset


@overload
def list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["BenchmarkExecutionExportMetadata"]: ...


def list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["BenchmarkExecutionExportMetadata"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["include_archived"] = include_archived

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/executions/metadata",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["BenchmarkExecutionExportMetadata"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['BenchmarkExecutionExportMetadata']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = BenchmarkExecutionExportMetadata.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from ..models import Benchmark, UpdateBenchmarkPayload


def update_benchmark_benchmarks__benchmark_uid__put(
    benchmark_uid: int,
    *,
    body: UpdateBenchmarkPayload,
) -> Benchmark:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Benchmark:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Benchmark
        response_200 = Benchmark.from_dict(response)

        return response_200

    return _parse_response(response)
