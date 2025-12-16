# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import Group


def create_group_scim_v2_Groups_post(
    *,
    body: Group,
) -> Group:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/Groups",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Group:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Group
        response_201 = Group.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_group_scim_v2_Groups__group_uid_str__delete(
    group_uid_str: str,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Groups/{group_uid_str}",
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

from ..models import Group


@overload
def get_group_scim_v2_Groups__group_uid_str__get(
    group_uid_str: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_group_scim_v2_Groups__group_uid_str__get(
    group_uid_str: str, raw: Literal[False] = False
) -> Group: ...


def get_group_scim_v2_Groups__group_uid_str__get(
    group_uid_str: str, raw: bool = False
) -> Group | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Groups/{group_uid_str}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Group:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Group
        response_200 = Group.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import ListResponseGroup
from ..types import UNSET, Unset


@overload
def list_groups_scim_v2_Groups_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_groups_scim_v2_Groups_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> ListResponseGroup: ...


def list_groups_scim_v2_Groups_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> ListResponseGroup | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["start_index"] = start_index

    params["count"] = count

    params["filter"] = filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/Groups",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListResponseGroup:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListResponseGroup
        response_200 = ListResponseGroup.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import Group, PatchOp


def patch_group_scim_v2_Groups__group_uid_str__patch(
    group_uid_str: str,
    *,
    body: PatchOp,
) -> Group:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Groups/{group_uid_str}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Group:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Group
        response_200 = Group.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import Group


def put_group_scim_v2_Groups__group_uid_str__put(
    group_uid_str: str,
    *,
    body: Group,
) -> Group:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Groups/{group_uid_str}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Group:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Group
        response_200 = Group.from_dict(response)

        return response_200

    return _parse_response(response)
