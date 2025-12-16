# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..types import UNSET, Unset


@overload
def export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    connector_config_uid: Union[Unset, int] = UNSET,
    destination_path: Union[Unset, str] = "",
    export_format: Union[Unset, str] = "json",
    sep: Union[Unset, str] = ",",
    quotechar: Union[Unset, str] = '\\"',
    escapechar: Union[Unset, str] = "\\",
    raw: Literal[True],
) -> requests.Response: ...


@overload
def export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    connector_config_uid: Union[Unset, int] = UNSET,
    destination_path: Union[Unset, str] = "",
    export_format: Union[Unset, str] = "json",
    sep: Union[Unset, str] = ",",
    quotechar: Union[Unset, str] = '\\"',
    escapechar: Union[Unset, str] = "\\",
    raw: Literal[False] = False,
) -> Any: ...


def export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    connector_config_uid: Union[Unset, int] = UNSET,
    destination_path: Union[Unset, str] = "",
    export_format: Union[Unset, str] = "json",
    sep: Union[Unset, str] = ",",
    quotechar: Union[Unset, str] = '\\"',
    escapechar: Union[Unset, str] = "\\",
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["connector_config_uid"] = connector_config_uid

    params["destination_path"] = destination_path

    params["export_format"] = export_format

    params["sep"] = sep

    params["quotechar"] = quotechar

    params["escapechar"] = escapechar

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/execution/{benchmark_execution_uid}/export",
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import DataFrameResponse
from ..types import UNSET, Unset


@overload
def get_dataframe_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__dataframe_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_dataframe_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__dataframe_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> DataFrameResponse: ...


def get_dataframe_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__dataframe_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> DataFrameResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["filter_config_str"] = filter_config_str

    params["split"] = split

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/execution/{benchmark_execution_uid}/dataframe",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataFrameResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataFrameResponse
        response_200 = DataFrameResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, cast, overload

import requests
from typing_extensions import Literal


@overload
def get_dataset_uid_by_benchmark_benchmarks__benchmark_uid__dataset_uid_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_dataset_uid_by_benchmark_benchmarks__benchmark_uid__dataset_uid_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> int: ...


def get_dataset_uid_by_benchmark_benchmarks__benchmark_uid__dataset_uid_get(
    benchmark_uid: int, raw: bool = False
) -> int | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/dataset_uid",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> int:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as int
        # Direct parsing for int
        return cast(int, response)

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import EvaluationScore
from ..types import UNSET, Unset


@overload
def get_scores_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__scores_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_scores_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__scores_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[False] = False,
) -> List["EvaluationScore"]: ...


def get_scores_by_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__scores_get(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: bool = False,
) -> List["EvaluationScore"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/execution/{benchmark_execution_uid}/scores",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["EvaluationScore"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['EvaluationScore']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = EvaluationScore.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    BenchmarkExecution,
    UpdateBenchmarkExecutionPayload,
)


def update_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__put(
    benchmark_uid: int,
    benchmark_execution_uid: int,
    *,
    body: UpdateBenchmarkExecutionPayload,
) -> BenchmarkExecution:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/execution/{benchmark_execution_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> BenchmarkExecution:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BenchmarkExecution
        response_200 = BenchmarkExecution.from_dict(response)

        return response_200

    return _parse_response(response)
