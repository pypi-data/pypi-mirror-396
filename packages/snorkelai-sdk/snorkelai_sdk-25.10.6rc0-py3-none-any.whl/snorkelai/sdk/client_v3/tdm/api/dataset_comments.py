# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateDatasetCommentParams,
    DatasetCommentResponse,
)


def create_comment_dataset__dataset_uid__comments_post(
    dataset_uid: int,
    *,
    body: CreateDatasetCommentParams,
) -> DatasetCommentResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/comments",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetCommentResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetCommentResponse
        response_201 = DatasetCommentResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_comment_dataset__dataset_uid__comments__comment_uid__delete(
    dataset_uid: int,
    comment_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/comments/{comment_uid}",
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

from ..models import DatasetCommentResponse


@overload
def get_comment_dataset__dataset_uid__comments__comment_uid__get(
    dataset_uid: int, comment_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_comment_dataset__dataset_uid__comments__comment_uid__get(
    dataset_uid: int, comment_uid: int, raw: Literal[False] = False
) -> DatasetCommentResponse: ...


def get_comment_dataset__dataset_uid__comments__comment_uid__get(
    dataset_uid: int, comment_uid: int, raw: bool = False
) -> DatasetCommentResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/comments/{comment_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetCommentResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetCommentResponse
        response_200 = DatasetCommentResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List

from ..models import (
    DatasetCommentsByXuidResponse,
    GetCommentsByXuidParams,
)


def get_comment_map_dataset__dataset_uid__get_comment_map_post(
    dataset_uid: int,
    *,
    body: GetCommentsByXuidParams,
) -> List["DatasetCommentsByXuidResponse"]:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/get-comment-map",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetCommentsByXuidResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetCommentsByXuidResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetCommentsByXuidResponse.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetCommentResponse
from ..types import UNSET, Unset


@overload
def list_comments_dataset__dataset_uid__comments_get(
    dataset_uid: int,
    *,
    user_uid: Union[Unset, int] = UNSET,
    body: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_comments_dataset__dataset_uid__comments_get(
    dataset_uid: int,
    *,
    user_uid: Union[Unset, int] = UNSET,
    body: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> List["DatasetCommentResponse"]: ...


def list_comments_dataset__dataset_uid__comments_get(
    dataset_uid: int,
    *,
    user_uid: Union[Unset, int] = UNSET,
    body: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> List["DatasetCommentResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["user_uid"] = user_uid

    params["body"] = body

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/comments",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetCommentResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetCommentResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetCommentResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import DatasetCommentResponse
from ..types import UNSET


def update_comment_dataset__dataset_uid__comments__comment_uid__put(
    dataset_uid: int,
    comment_uid: int,
    *,
    updated_body: str,
) -> DatasetCommentResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["updated_body"] = updated_body

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/comments/{comment_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetCommentResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetCommentResponse
        response_200 = DatasetCommentResponse.from_dict(response)

        return response_200

    return _parse_response(response)
