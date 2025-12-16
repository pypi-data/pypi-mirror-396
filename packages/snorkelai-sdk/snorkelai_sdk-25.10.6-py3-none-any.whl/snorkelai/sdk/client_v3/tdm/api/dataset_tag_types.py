# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateDatasetTagTypeParams, DatasetTagType


def create_tag_type_dataset__dataset_uid__tag_type_post(
    dataset_uid: int,
    *,
    body: CreateDatasetTagTypeParams,
) -> DatasetTagType:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/tag-type",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetTagType:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetTagType
        response_201 = DatasetTagType.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_tag_type_dataset__dataset_uid__tag_type__tag_type_uid__delete(
    dataset_uid: int,
    tag_type_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/tag-type/{tag_type_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import (
    GetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPostResponseGetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPost,
    GetTagMapReq,
)


def get_dataset_tag_mapping_dataset__dataset_uid__get_dataset_tag_map_post(
    dataset_uid: int,
    *,
    body: GetTagMapReq,
) -> GetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPostResponseGetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPost:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/get-dataset-tag-map",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPostResponseGetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPost:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPostResponseGetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPost
        response_200 = GetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPostResponseGetDatasetTagMappingDatasetDatasetUidGetDatasetTagMapPost.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DatasetTagType


@overload
def get_tag_type_dataset__dataset_uid__tag_type__tag_type_uid__get(
    dataset_uid: int, tag_type_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_tag_type_dataset__dataset_uid__tag_type__tag_type_uid__get(
    dataset_uid: int, tag_type_uid: int, raw: Literal[False] = False
) -> DatasetTagType: ...


def get_tag_type_dataset__dataset_uid__tag_type__tag_type_uid__get(
    dataset_uid: int, tag_type_uid: int, raw: bool = False
) -> DatasetTagType | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/tag-type/{tag_type_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetTagType:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetTagType
        response_200 = DatasetTagType.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetTagType
from ..types import UNSET, Unset


@overload
def get_tag_types_dataset__dataset_uid__tag_type_get(
    dataset_uid: int,
    *,
    is_context_tag_type: Union[Unset, bool] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_tag_types_dataset__dataset_uid__tag_type_get(
    dataset_uid: int,
    *,
    is_context_tag_type: Union[Unset, bool] = UNSET,
    raw: Literal[False] = False,
) -> List["DatasetTagType"]: ...


def get_tag_types_dataset__dataset_uid__tag_type_get(
    dataset_uid: int,
    *,
    is_context_tag_type: Union[Unset, bool] = UNSET,
    raw: bool = False,
) -> List["DatasetTagType"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["is_context_tag_type"] = is_context_tag_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/tag-type",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetTagType"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetTagType']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetTagType.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateTagMapReq


def update_dataset_tag_mapping_dataset__dataset_uid__update_dataset_tag_map_post(
    dataset_uid: int,
    *,
    body: UpdateTagMapReq,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/update-dataset-tag-map",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import DatasetTagType, UpdateTagType


def update_tag_type_dataset__dataset_uid__tag_type__tag_type_uid__put(
    dataset_uid: int,
    tag_type_uid: int,
    *,
    body: UpdateTagType,
) -> DatasetTagType:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/tag-type/{tag_type_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetTagType:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetTagType
        response_200 = DatasetTagType.from_dict(response)

        return response_200

    return _parse_response(response)
