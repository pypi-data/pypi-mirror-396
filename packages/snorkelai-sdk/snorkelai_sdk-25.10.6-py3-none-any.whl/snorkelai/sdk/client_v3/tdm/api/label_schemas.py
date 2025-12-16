# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CopyLabelSchemaPayload


def copy_label_schema_label_schemas__label_schema_uid__post(
    label_schema_uid: int,
    *,
    body: CopyLabelSchemaPayload,
) -> str:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/label-schemas/{label_schema_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> str:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as str
        # Direct parsing for str
        return cast(str, response)

    return _parse_response(response)


from ..models import (
    CreateLabelSchemaPayload,
    CreateLabelSchemaResponse,
)


def create_label_schema_label_schemas_post(
    *,
    body: CreateLabelSchemaPayload,
) -> CreateLabelSchemaResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/label-schemas",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateLabelSchemaResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateLabelSchemaResponse
        response_201 = CreateLabelSchemaResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_label_schema(
    label_schema_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/label-schemas/{label_schema_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import LabelSchema


@overload
def list_label_schemas_by_batch_batch__dataset_batch_uid__label_schemas_get(
    dataset_batch_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_label_schemas_by_batch_batch__dataset_batch_uid__label_schemas_get(
    dataset_batch_uid: int, raw: Literal[False] = False
) -> List["LabelSchema"]: ...


def list_label_schemas_by_batch_batch__dataset_batch_uid__label_schemas_get(
    dataset_batch_uid: int, raw: bool = False
) -> List["LabelSchema"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/batch/{dataset_batch_uid}/label-schemas",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["LabelSchema"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['LabelSchema']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = LabelSchema.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def list_label_schemas_label_schemas_get(
    *,
    name: Union[Unset, str] = UNSET,
    label_schema_uid: Union[Unset, int] = UNSET,
    dataset_uid: Union[Unset, int] = UNSET,
    include_metadata: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_label_schemas_label_schemas_get(
    *,
    name: Union[Unset, str] = UNSET,
    label_schema_uid: Union[Unset, int] = UNSET,
    dataset_uid: Union[Unset, int] = UNSET,
    include_metadata: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["LabelSchema"]: ...


def list_label_schemas_label_schemas_get(
    *,
    name: Union[Unset, str] = UNSET,
    label_schema_uid: Union[Unset, int] = UNSET,
    dataset_uid: Union[Unset, int] = UNSET,
    include_metadata: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["LabelSchema"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["name"] = name

    params["label_schema_uid"] = label_schema_uid

    params["dataset_uid"] = dataset_uid

    params["include_metadata"] = include_metadata

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/label-schemas",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["LabelSchema"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['LabelSchema']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = LabelSchema.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateLabelSchemaPayload


def update_label_schema_label_schemas__label_schema_uid__put(
    label_schema_uid: int,
    *,
    body: UpdateLabelSchemaPayload,
) -> LabelSchema:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/label-schemas/{label_schema_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> LabelSchema:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as LabelSchema
        response_201 = LabelSchema.from_dict(response)

        return response_201

    return _parse_response(response)
