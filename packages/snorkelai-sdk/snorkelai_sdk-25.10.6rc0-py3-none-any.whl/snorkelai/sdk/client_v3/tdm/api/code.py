# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    ExecuteCodeVersionRequest,
    ExecuteCodeVersionResponse,
)


def execute_code_version_code_version__code_version_uid__execute_post(
    code_version_uid: int,
    *,
    body: ExecuteCodeVersionRequest,
) -> ExecuteCodeVersionResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/code_version/{code_version_uid}/execute",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ExecuteCodeVersionResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ExecuteCodeVersionResponse
        response_201 = ExecuteCodeVersionResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import CodeExecution


@overload
def get_code_execution_code_execution__code_execution_uid__get(
    code_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_code_execution_code_execution__code_execution_uid__get(
    code_execution_uid: int, raw: Literal[False] = False
) -> CodeExecution: ...


def get_code_execution_code_execution__code_execution_uid__get(
    code_execution_uid: int, raw: bool = False
) -> CodeExecution | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/code_execution/{code_execution_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> CodeExecution:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CodeExecution
        response_200 = CodeExecution.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import GetCodeExecutionResultsResponse


@overload
def get_code_execution_results_code_execution__code_execution_uid__results_get(
    code_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_code_execution_results_code_execution__code_execution_uid__results_get(
    code_execution_uid: int, raw: Literal[False] = False
) -> GetCodeExecutionResultsResponse: ...


def get_code_execution_results_code_execution__code_execution_uid__results_get(
    code_execution_uid: int, raw: bool = False
) -> GetCodeExecutionResultsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/code_execution/{code_execution_uid}/results",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetCodeExecutionResultsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetCodeExecutionResultsResponse
        response_200 = GetCodeExecutionResultsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import CodeExecution


@overload
def list_code_executions_by_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__executions_get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_code_executions_by_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__executions_get(
    benchmark_uid: int,
    criteria_uid: int,
    evaluator_uid: int,
    raw: Literal[False] = False,
) -> List["CodeExecution"]: ...


def list_code_executions_by_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__executions_get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: bool = False
) -> List["CodeExecution"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/code/{evaluator_uid}/executions",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["CodeExecution"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['CodeExecution']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = CodeExecution.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import CodeExecution


@overload
def list_code_executions_code_version__code_version_uid__executions_get(
    code_version_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_code_executions_code_version__code_version_uid__executions_get(
    code_version_uid: int, raw: Literal[False] = False
) -> List["CodeExecution"]: ...


def list_code_executions_code_version__code_version_uid__executions_get(
    code_version_uid: int, raw: bool = False
) -> List["CodeExecution"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/code_version/{code_version_uid}/executions",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["CodeExecution"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['CodeExecution']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = CodeExecution.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import CodeVersion


@overload
def list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
    benchmark_uid: int,
    criteria_uid: int,
    evaluator_uid: int,
    raw: Literal[False] = False,
) -> List["CodeVersion"]: ...


def list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: bool = False
) -> List["CodeVersion"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/code/{evaluator_uid}/versions",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["CodeVersion"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['CodeVersion']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = CodeVersion.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)
