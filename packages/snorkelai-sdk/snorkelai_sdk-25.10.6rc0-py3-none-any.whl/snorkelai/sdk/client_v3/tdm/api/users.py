# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import ChangePassword


def change_password_change_password_post(
    *,
    body: ChangePassword,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/change-password",
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

from ..models import CreateUserRequest, UserResponse


def create_user_users_post(
    *,
    body: CreateUserRequest,
) -> UserResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/users",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserResponse
        response_201 = UserResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import GetAccessTokenRequest, TokenPair


def get_access_token_get_token_post(
    *,
    body: GetAccessTokenRequest,
) -> TokenPair:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/get-token",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> TokenPair:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as TokenPair
        response_200 = TokenPair.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import GetCurrentUserResponse
from ..types import UNSET, Unset


@overload
def get_current_user_current_user_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_current_user_current_user_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: Literal[False] = False
) -> GetCurrentUserResponse: ...


def get_current_user_current_user_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: bool = False
) -> GetCurrentUserResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/current-user",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetCurrentUserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetCurrentUserResponse
        response_200 = GetCurrentUserResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import HeaderTokenResponse


@overload
def get_header_token_header_token_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_header_token_header_token_get(
    raw: Literal[False] = False,
) -> HeaderTokenResponse: ...


def get_header_token_header_token_get(
    raw: bool = False,
) -> HeaderTokenResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/header-token",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> HeaderTokenResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as HeaderTokenResponse
        response_200 = HeaderTokenResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import JWTSigningInfo


@overload
def get_jwt_signing_info_jwt_signing_info_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_jwt_signing_info_jwt_signing_info_get(
    raw: Literal[False] = False,
) -> JWTSigningInfo: ...


def get_jwt_signing_info_jwt_signing_info_get(
    raw: bool = False,
) -> JWTSigningInfo | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/jwt-signing-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> JWTSigningInfo:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as JWTSigningInfo
        response_200 = JWTSigningInfo.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import ListUserResponse
from ..types import Unset


@overload
def get_list_users_users_get(
    *,
    include_inactive: Union[Unset, bool] = False,
    include_superadmins: Union[Unset, bool] = False,
    workspace_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_list_users_users_get(
    *,
    include_inactive: Union[Unset, bool] = False,
    include_superadmins: Union[Unset, bool] = False,
    workspace_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> List["ListUserResponse"]: ...


def get_list_users_users_get(
    *,
    include_inactive: Union[Unset, bool] = False,
    include_superadmins: Union[Unset, bool] = False,
    workspace_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> List["ListUserResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["include_inactive"] = include_inactive

    params["include_superadmins"] = include_superadmins

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/users",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["ListUserResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['ListUserResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = ListUserResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def get_list_workspaced_users_workspaced_users_get(
    *,
    workspace_uid: int,
    include_inactive: Union[Unset, bool] = True,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_list_workspaced_users_workspaced_users_get(
    *,
    workspace_uid: int,
    include_inactive: Union[Unset, bool] = True,
    raw: Literal[False] = False,
) -> List["ListUserResponse"]: ...


def get_list_workspaced_users_workspaced_users_get(
    *,
    workspace_uid: int,
    include_inactive: Union[Unset, bool] = True,
    raw: bool = False,
) -> List["ListUserResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["include_inactive"] = include_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workspaced-users",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["ListUserResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['ListUserResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = ListUserResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import RefreshToken, RefreshTokenResponse


def refresh_token_refresh_token_post(
    *,
    body: RefreshToken,
) -> RefreshTokenResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/refresh-token",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> RefreshTokenResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RefreshTokenResponse
        response_200 = RefreshTokenResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any


def remove_user_users__user_uid__delete(
    user_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}",
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

from ..models import ResetPasswordParams


def reset_password_reset_password_post(
    *,
    body: ResetPasswordParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/reset-password",
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

from ..models import UpdateUserEmail, UserResponse


def update_user_email_users__user_uid__email_put(
    user_uid: int,
    *,
    body: UpdateUserEmail,
) -> UserResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/email",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserResponse
        response_200 = UserResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateUserRole, UserResponse


def update_user_role_users__user_uid__role_put(
    user_uid: int,
    *,
    body: UpdateUserRole,
) -> UserResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/role",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserResponse
        response_200 = UserResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateUserTimezone, UserResponse


def update_user_timezone_users__user_uid__timezone_put(
    user_uid: int,
    *,
    body: UpdateUserTimezone,
) -> UserResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/timezone",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserResponse
        response_200 = UserResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateUserPayload


def update_user_users__user_uid__put(
    user_uid: int,
    *,
    body: UpdateUserPayload,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}",
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


from typing import Any

from ..models import UpdateUserView, UserResponse


def update_user_view_users__user_uid__default_view_put(
    user_uid: int,
    *,
    body: UpdateUserView,
) -> UserResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/default-view",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserResponse
        response_200 = UserResponse.from_dict(response)

        return response_200

    return _parse_response(response)
