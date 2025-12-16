# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateCriteriaPayload, Criteria


def create_criteria_benchmarks__benchmark_uid__criteria_post(
    benchmark_uid: int,
    *,
    body: CreateCriteriaPayload,
) -> Criteria:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Criteria:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Criteria
        response_201 = Criteria.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import List

from ..models import CreateSelectedDefaultCriteriaPayload, Criteria


def create_default_criteria_benchmarks__benchmark_uid__default_criteria_post(
    benchmark_uid: int,
    *,
    body: CreateSelectedDefaultCriteriaPayload,
) -> List["Criteria"]:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/default-criteria",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> List["Criteria"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Criteria']
        response_201 = []
        _response_201 = response
        for response_201_item_data in _response_201:
            response_201_item = Criteria.from_dict(response_201_item_data)

            response_201.append(response_201_item)

        return response_201

    return _parse_response(response)


from typing import cast, overload

import requests
from typing_extensions import Literal


@overload
def get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
    criteria_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
    criteria_uid: int, raw: Literal[False] = False
) -> int: ...


def get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
    criteria_uid: int, raw: bool = False
) -> int | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/criteria/{criteria_uid}/benchmark_uid",
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


from typing import overload

import requests
from typing_extensions import Literal

from ..models import Criteria


@overload
def get_criteria_by_uid_benchmarks__benchmark_uid__criteria__criteria_uid__get(
    benchmark_uid: int, criteria_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_criteria_by_uid_benchmarks__benchmark_uid__criteria__criteria_uid__get(
    benchmark_uid: int, criteria_uid: int, raw: Literal[False] = False
) -> Criteria: ...


def get_criteria_by_uid_benchmarks__benchmark_uid__criteria__criteria_uid__get(
    benchmark_uid: int, criteria_uid: int, raw: bool = False
) -> Criteria | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Criteria:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Criteria
        response_200 = Criteria.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import Criteria
from ..types import UNSET, Unset


@overload
def get_criteria_for_benchmark_benchmarks__benchmark_uid__criteria_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_criteria_for_benchmark_benchmarks__benchmark_uid__criteria_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["Criteria"]: ...


def get_criteria_for_benchmark_benchmarks__benchmark_uid__criteria_get(
    benchmark_uid: int,
    *,
    include_archived: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["Criteria"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["include_archived"] = include_archived

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Criteria"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Criteria']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Criteria.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import EvaluatorCriteriaConfig
from ..types import Unset


@overload
def get_default_criteria_templates_benchmarks_defaults_templates_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_default_criteria_templates_benchmarks_defaults_templates_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: Literal[False] = False
) -> List["EvaluatorCriteriaConfig"]: ...


def get_default_criteria_templates_benchmarks_defaults_templates_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: bool = False
) -> List["EvaluatorCriteriaConfig"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks/defaults/templates",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["EvaluatorCriteriaConfig"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['EvaluatorCriteriaConfig']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = EvaluatorCriteriaConfig.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from ..models import Criteria, UpdateCriteriaPayload


def update_criteria_benchmarks__benchmark_uid__criteria__criteria_uid__put(
    benchmark_uid: int,
    criteria_uid: int,
    *,
    body: UpdateCriteriaPayload,
) -> Criteria:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Criteria:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Criteria
        response_200 = Criteria.from_dict(response)

        return response_200

    return _parse_response(response)
