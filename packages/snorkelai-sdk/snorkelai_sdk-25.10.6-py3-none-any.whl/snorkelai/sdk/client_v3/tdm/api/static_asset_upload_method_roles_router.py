# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import StaticAssetUploadMethodRoleCreationRequest


def create_static_asset_upload_method_role_static_asset_upload_method_roles_post(
    *,
    body: StaticAssetUploadMethodRoleCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset-upload-method-roles",
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


def delete_static_asset_upload_method_role_static_asset_upload_method_roles__role_uid__delete(
    role_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/static-asset-upload-method-roles/{role_uid}",
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

from ..models import StaticAssetUploadMethod


@overload
def get_static_asset_upload_method_role_static_asset_upload_method_roles__role_uid__get(
    role_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_static_asset_upload_method_role_static_asset_upload_method_roles__role_uid__get(
    role_uid: int, raw: Literal[False] = False
) -> StaticAssetUploadMethod: ...


def get_static_asset_upload_method_role_static_asset_upload_method_roles__role_uid__get(
    role_uid: int, raw: bool = False
) -> StaticAssetUploadMethod | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/static-asset-upload-method-roles/{role_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> StaticAssetUploadMethod:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as StaticAssetUploadMethod
        response_200 = StaticAssetUploadMethod(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet,
    StaticAssetUploadMethod,
)
from ..types import UNSET, Unset


@overload
def list_static_asset_upload_method_roles_static_asset_upload_method_roles_get(
    *,
    static_asset_upload_method: Union[Unset, StaticAssetUploadMethod] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_static_asset_upload_method_roles_static_asset_upload_method_roles_get(
    *,
    static_asset_upload_method: Union[Unset, StaticAssetUploadMethod] = UNSET,
    raw: Literal[False] = False,
) -> ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet: ...


def list_static_asset_upload_method_roles_static_asset_upload_method_roles_get(
    *,
    static_asset_upload_method: Union[Unset, StaticAssetUploadMethod] = UNSET,
    raw: bool = False,
) -> (
    ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_static_asset_upload_method: Union[Unset, str] = UNSET
    if not isinstance(static_asset_upload_method, Unset):
        json_static_asset_upload_method = static_asset_upload_method.value

    params["static_asset_upload_method"] = json_static_asset_upload_method

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset-upload-method-roles",
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
    ) -> ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet
        response_200 = ListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGetResponseListStaticAssetUploadMethodRolesStaticAssetUploadMethodRolesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
