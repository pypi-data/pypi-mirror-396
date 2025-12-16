# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateUserScimV2UsersPostResponseCreateUserScimV2UsersPost,
    CreateUserScimV2UsersPostScimUserDict,
)


def create_user_scim_v2_Users_post(
    *,
    body: CreateUserScimV2UsersPostScimUserDict,
) -> CreateUserScimV2UsersPostResponseCreateUserScimV2UsersPost:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/Users",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> CreateUserScimV2UsersPostResponseCreateUserScimV2UsersPost:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateUserScimV2UsersPostResponseCreateUserScimV2UsersPost
        response_200 = (
            CreateUserScimV2UsersPostResponseCreateUserScimV2UsersPost.from_dict(
                response
            )
        )

        return response_200

    return _parse_response(response)


def delete_user_scim_v2_Users__user_uid_str__delete(
    user_uid_str: str,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Users/{user_uid_str}",
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

from ..models import (
    GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet,
)


@overload
def get_user_scim_v2_Users__user_uid_str__get(
    user_uid_str: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_user_scim_v2_Users__user_uid_str__get(
    user_uid_str: str, raw: Literal[False] = False
) -> GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet: ...


def get_user_scim_v2_Users__user_uid_str__get(
    user_uid_str: str, raw: bool = False
) -> (
    GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Users/{user_uid_str}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet
        response_200 = GetUserScimV2UsersUserUidStrGetResponseGetUserScimV2UsersUserUidStrGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet,
)
from ..types import UNSET, Unset


@overload
def list_users_scim_v2_Users_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_users_scim_v2_Users_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet: ...


def list_users_scim_v2_Users_get(
    *,
    start_index: Union[Unset, int] = UNSET,
    count: Union[Unset, int] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["start_index"] = start_index

    params["count"] = count

    params["filter"] = filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/Users",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet
        response_200 = ListUsersScimV2UsersGetResponseListUsersScimV2UsersGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    PatchUserScimV2UsersUserUidStrPatchPatchOpDict,
    PatchUserScimV2UsersUserUidStrPatchResponsePatchUserScimV2UsersUserUidStrPatch,
)


def patch_user_scim_v2_Users__user_uid_str__patch(
    user_uid_str: str,
    *,
    body: PatchUserScimV2UsersUserUidStrPatchPatchOpDict,
) -> PatchUserScimV2UsersUserUidStrPatchResponsePatchUserScimV2UsersUserUidStrPatch:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Users/{user_uid_str}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> PatchUserScimV2UsersUserUidStrPatchResponsePatchUserScimV2UsersUserUidStrPatch:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PatchUserScimV2UsersUserUidStrPatchResponsePatchUserScimV2UsersUserUidStrPatch
        response_200 = PatchUserScimV2UsersUserUidStrPatchResponsePatchUserScimV2UsersUserUidStrPatch.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    PutUserScimV2UsersUserUidStrPutResponsePutUserScimV2UsersUserUidStrPut,
    PutUserScimV2UsersUserUidStrPutScimUserDict,
)


def put_user_scim_v2_Users__user_uid_str__put(
    user_uid_str: str,
    *,
    body: PutUserScimV2UsersUserUidStrPutScimUserDict,
) -> PutUserScimV2UsersUserUidStrPutResponsePutUserScimV2UsersUserUidStrPut:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Users/{user_uid_str}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> PutUserScimV2UsersUserUidStrPutResponsePutUserScimV2UsersUserUidStrPut:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PutUserScimV2UsersUserUidStrPutResponsePutUserScimV2UsersUserUidStrPut
        response_200 = PutUserScimV2UsersUserUidStrPutResponsePutUserScimV2UsersUserUidStrPut.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
