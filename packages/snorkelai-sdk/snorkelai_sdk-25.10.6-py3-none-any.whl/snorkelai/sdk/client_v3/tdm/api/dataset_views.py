# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateDatasetViewParams, DatasetView


def create_dataset_view_dataset__dataset_uid__views_post(
    dataset_uid: int,
    *,
    body: CreateDatasetViewParams,
) -> DatasetView:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/views",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetView:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetView
        response_201 = DatasetView.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_dataset_view_dataset_views__dataset_view_uid__delete(
    dataset_view_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/views/{dataset_view_uid}",
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

from ..models import DatasetView


@overload
def get_dataset_view_dataset_views__dataset_view_uid__get(
    dataset_view_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_dataset_view_dataset_views__dataset_view_uid__get(
    dataset_view_uid: int, raw: Literal[False] = False
) -> DatasetView: ...


def get_dataset_view_dataset_views__dataset_view_uid__get(
    dataset_view_uid: int, raw: bool = False
) -> DatasetView | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/views/{dataset_view_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetView:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetView
        response_200 = DatasetView.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetView
from ..types import UNSET, Unset


@overload
def get_dataset_views_dataset__dataset_uid__views_get(
    dataset_uid: int,
    *,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    add_views_without_ls: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_dataset_views_dataset__dataset_uid__views_get(
    dataset_uid: int,
    *,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    add_views_without_ls: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["DatasetView"]: ...


def get_dataset_views_dataset__dataset_uid__views_get(
    dataset_uid: int,
    *,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    add_views_without_ls: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["DatasetView"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_label_schema_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(label_schema_uids, Unset):
        json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    params["add_views_without_ls"] = add_views_without_ls

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/views",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetView"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetView']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetView.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import DatasetViewUpdateParams


def update_dataset_view_dataset_views__dataset_view_uid__put(
    dataset_view_uid: int,
    *,
    body: DatasetViewUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/views/{dataset_view_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
