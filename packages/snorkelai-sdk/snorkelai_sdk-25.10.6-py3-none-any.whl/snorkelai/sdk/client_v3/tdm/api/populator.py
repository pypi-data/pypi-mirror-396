# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    ApplyBenchmarkPopulatorRequest,
    ApplyBenchmarkPopulatorResponse,
)


def apply_populator_benchmarks_populators_apply_post(
    *,
    body: ApplyBenchmarkPopulatorRequest,
) -> ApplyBenchmarkPopulatorResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks/populators/apply",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ApplyBenchmarkPopulatorResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ApplyBenchmarkPopulatorResponse
        response_202 = ApplyBenchmarkPopulatorResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from ..models import (
    CreateBenchmarkPopulatorRequest,
    CreateBenchmarkPopulatorResponse,
)


def create_populator_benchmarks_populators_create_post(
    *,
    body: CreateBenchmarkPopulatorRequest,
) -> CreateBenchmarkPopulatorResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks/populators/create",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateBenchmarkPopulatorResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateBenchmarkPopulatorResponse
        response_202 = CreateBenchmarkPopulatorResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import ListBenchmarkPopulatorsResponse


@overload
def list_populators_benchmarks_populators_list_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_populators_benchmarks_populators_list_get(
    raw: Literal[False] = False,
) -> ListBenchmarkPopulatorsResponse: ...


def list_populators_benchmarks_populators_list_get(
    raw: bool = False,
) -> ListBenchmarkPopulatorsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/benchmarks/populators/list",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListBenchmarkPopulatorsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListBenchmarkPopulatorsResponse
        response_200 = ListBenchmarkPopulatorsResponse.from_dict(response)

        return response_200

    return _parse_response(response)
