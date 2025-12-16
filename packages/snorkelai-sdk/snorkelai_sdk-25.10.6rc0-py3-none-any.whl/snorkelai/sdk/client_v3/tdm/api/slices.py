# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import ModifySliceRequest


def add_xuids_to_slice_dataset__dataset_uid__add_xuids__slice_uid__post(
    dataset_uid: int,
    slice_uid: int,
    *,
    body: ModifySliceRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/add-xuids/{slice_uid}",
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


from typing import Any, cast

from ..models import SliceCreationRequest


def create_slice_dataset__dataset_uid__slice_post(
    dataset_uid: int,
    *,
    body: SliceCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> int:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as int
        # Direct parsing for int
        return cast(int, response)

    return _parse_response(response)


from typing import Any


def delete_slice_dataset__dataset_uid__slice__slice_uid__delete(
    dataset_uid: int,
    slice_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice/{slice_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, List

from ..models import SliceOverrideDelete


def delete_slice_overrides_dataset__dataset_uid__slice_overrides_delete(
    dataset_uid: int,
    *,
    body: List["SliceOverrideDelete"],
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice-overrides",
    }

    _body = []
    for componentsschemas_slice_override_delete_list_item_data in body:
        componentsschemas_slice_override_delete_list_item = (
            componentsschemas_slice_override_delete_list_item_data.to_dict()
        )
        _body.append(componentsschemas_slice_override_delete_list_item)

    _kwargs["json"] = _body

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

from ..models import SliceWithConfig


@overload
def get_slice_dataset__dataset_uid__slice__slice_uid__get(
    dataset_uid: int, slice_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_slice_dataset__dataset_uid__slice__slice_uid__get(
    dataset_uid: int, slice_uid: int, raw: Literal[False] = False
) -> SliceWithConfig: ...


def get_slice_dataset__dataset_uid__slice__slice_uid__get(
    dataset_uid: int, slice_uid: int, raw: bool = False
) -> SliceWithConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice/{slice_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> SliceWithConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SliceWithConfig
        response_200 = SliceWithConfig.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal


@overload
def get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get(
    dataset_uid: int, slice_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get(
    dataset_uid: int, slice_uid: int, raw: Literal[False] = False
) -> List[str]: ...


def get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get(
    dataset_uid: int, slice_uid: int, raw: bool = False
) -> List[str] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice/{slice_uid}/membership",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List[str]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[str]
        response_200 = cast(List[str], response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    GetSliceMembershipRequest,
    SliceMembershipResponse,
)


def get_slice_membership_new_dataset__dataset_uid__get_slice_membership_and_overrides_post(
    dataset_uid: int,
    *,
    body: GetSliceMembershipRequest,
) -> SliceMembershipResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/get-slice-membership-and-overrides",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SliceMembershipResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SliceMembershipResponse
        response_200 = SliceMembershipResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    GetSliceMapRequest,
    GetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPostResponseGetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPost,
)


def get_slice_xuids_dataset__dataset_uid__get_xuid_to_slice_map_post(
    dataset_uid: int,
    *,
    body: GetSliceMapRequest,
) -> GetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPostResponseGetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPost:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/get-xuid-to-slice-map",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPostResponseGetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPost:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPostResponseGetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPost
        response_200 = GetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPostResponseGetSliceXuidsDatasetDatasetUidGetXuidToSliceMapPost.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import SliceCollectionItem


@overload
def get_slices_collection_dataset__dataset_uid__slices_collection_get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_slices_collection_dataset__dataset_uid__slices_collection_get(
    dataset_uid: int, raw: Literal[False] = False
) -> List["SliceCollectionItem"]: ...


def get_slices_collection_dataset__dataset_uid__slices_collection_get(
    dataset_uid: int, raw: bool = False
) -> List["SliceCollectionItem"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slices-collection",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["SliceCollectionItem"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['SliceCollectionItem']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = SliceCollectionItem.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import SliceWithConfig


@overload
def get_slices_dataset__dataset_uid__slices_get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_slices_dataset__dataset_uid__slices_get(
    dataset_uid: int, raw: Literal[False] = False
) -> List["SliceWithConfig"]: ...


def get_slices_dataset__dataset_uid__slices_get(
    dataset_uid: int, raw: bool = False
) -> List["SliceWithConfig"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slices",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["SliceWithConfig"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['SliceWithConfig']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = SliceWithConfig.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import ModifySliceRequest


def remove_xuids_from_slice_dataset__dataset_uid__remove_xuids__slice_uid__post(
    dataset_uid: int,
    slice_uid: int,
    *,
    body: ModifySliceRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/remove-xuids/{slice_uid}",
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

from ..models import Membership
from ..types import UNSET


def set_slice_membership_dataset__dataset_uid__x_uid__x_uid__slice_uid__slice_uid__slice_membership_put(
    dataset_uid: int,
    x_uid: str,
    slice_uid: int,
    *,
    membership: Membership,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_membership = membership.value
    params["membership"] = json_membership

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/x-uid/{x_uid}/slice-uid/{slice_uid}/slice-membership",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import SliceWithConfig, UpdateSliceRequest


def update_slice_dataset__dataset_uid__slice__slice_uid__put(
    dataset_uid: int,
    slice_uid: int,
    *,
    body: UpdateSliceRequest,
) -> SliceWithConfig:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/slice/{slice_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SliceWithConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SliceWithConfig
        response_200 = SliceWithConfig.from_dict(response)

        return response_200

    return _parse_response(response)
