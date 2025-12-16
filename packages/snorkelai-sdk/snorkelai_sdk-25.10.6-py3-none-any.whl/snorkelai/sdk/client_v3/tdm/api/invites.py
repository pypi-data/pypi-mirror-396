# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateInviteParams, InviteResponse


def create_invite_invite_post(
    *,
    body: CreateInviteParams,
) -> InviteResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/invite",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> InviteResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as InviteResponse
        response_201 = InviteResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import ExpireInviteParams


def expire_invite_invite_delete(
    *,
    body: ExpireInviteParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/invite",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

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

from ..models import GetInvitesResponse
from ..types import UNSET, Unset


@overload
def get_list_invites_invites_get(
    *, show_expired: Union[Unset, bool] = False, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_list_invites_invites_get(
    *, show_expired: Union[Unset, bool] = False, raw: Literal[False] = False
) -> GetInvitesResponse: ...


def get_list_invites_invites_get(
    *, show_expired: Union[Unset, bool] = False, raw: bool = False
) -> GetInvitesResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["show_expired"] = show_expired

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/invites",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetInvitesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetInvitesResponse
        response_200 = GetInvitesResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ValidateInviteResponse


@overload
def validate_invite_invite_validate_get(
    *, invite_link: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def validate_invite_invite_validate_get(
    *, invite_link: str, raw: Literal[False] = False
) -> ValidateInviteResponse: ...


def validate_invite_invite_validate_get(
    *, invite_link: str, raw: bool = False
) -> ValidateInviteResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["invite_link"] = invite_link

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/invite/validate",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ValidateInviteResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ValidateInviteResponse
        response_200 = ValidateInviteResponse.from_dict(response)

        return response_200

    return _parse_response(response)
