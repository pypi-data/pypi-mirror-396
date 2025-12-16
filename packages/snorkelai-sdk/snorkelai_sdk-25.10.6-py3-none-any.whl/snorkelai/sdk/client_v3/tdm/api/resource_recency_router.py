# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DatasetInfo
from ..types import UNSET


@overload
def get_recent_datasets_users__user_uid__recent_datasets_get(
    user_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_recent_datasets_users__user_uid__recent_datasets_get(
    user_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> List["DatasetInfo"]: ...


def get_recent_datasets_users__user_uid__recent_datasets_get(
    user_uid: int, *, workspace_uid: int, raw: bool = False
) -> List["DatasetInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/recent-datasets",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal


@overload
def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: Literal[False] = False
) -> List["DatasetInfo"]: ...


def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: bool = False
) -> List["DatasetInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspace/{workspace_uid}/recent-datasets",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


def view_dataset_users__user_uid__view_dataset__dataset_uid__post(
    user_uid: int,
    dataset_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/view-dataset/{dataset_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
