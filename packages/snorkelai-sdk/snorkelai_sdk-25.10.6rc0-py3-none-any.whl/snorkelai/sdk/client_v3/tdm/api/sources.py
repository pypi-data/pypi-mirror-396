# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import AddSourceParams, AddSourceResponse


def add_source_sources_post(
    *,
    body: AddSourceParams,
) -> AddSourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AddSourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AddSourceResponse
        response_201 = AddSourceResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_source_sources__source_uid__delete(
    source_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/sources/{source_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import GetSourcesResponse
from ..types import UNSET, Unset


@overload
def get_sources_sources_get(
    *,
    workspace_uid: Union[Unset, int] = UNSET,
    source_type: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_sources_sources_get(
    *,
    workspace_uid: Union[Unset, int] = UNSET,
    source_type: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> GetSourcesResponse: ...


def get_sources_sources_get(
    *,
    workspace_uid: Union[Unset, int] = UNSET,
    source_type: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> GetSourcesResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["source_type"] = source_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetSourcesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSourcesResponse
        response_200 = GetSourcesResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import Source, UpdateSourceParams


def update_source_sources__source_uid__put(
    source_uid: int,
    *,
    body: UpdateSourceParams,
) -> Source:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/sources/{source_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Source:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Source
        response_200 = Source.from_dict(response)

        return response_200

    return _parse_response(response)
