# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateOpVersionPayload,
    CreateOpVersionResponse,
)


def create_op_version_endpoint_nodes__node_uid__op_versions_post(
    node_uid: int,
    *,
    body: CreateOpVersionPayload,
) -> CreateOpVersionResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/op-versions",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateOpVersionResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateOpVersionResponse
        response_201 = CreateOpVersionResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_op_version_nodes__node_uid__op_versions__op_version_uid__delete(
    node_uid: int,
    op_version_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/op-versions/{op_version_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import OpVersion


@overload
def fetch_op_version_nodes__node_uid__op_versions__op_version_uid__get(
    node_uid: int, op_version_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_op_version_nodes__node_uid__op_versions__op_version_uid__get(
    node_uid: int, op_version_uid: int, raw: Literal[False] = False
) -> OpVersion: ...


def fetch_op_version_nodes__node_uid__op_versions__op_version_uid__get(
    node_uid: int, op_version_uid: int, raw: bool = False
) -> OpVersion | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/op-versions/{op_version_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> OpVersion:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as OpVersion
        response_200 = OpVersion.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, cast, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def list_op_versions_nodes__node_uid__op_versions_get(
    node_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_op_versions_nodes__node_uid__op_versions_get(
    node_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> List[int]: ...


def list_op_versions_nodes__node_uid__op_versions_get(
    node_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> List[int] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/op-versions",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List[int]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[int]
        response_200 = cast(List[int], response)

        return response_200

    return _parse_response(response)
