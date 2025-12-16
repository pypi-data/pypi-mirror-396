# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import StaticAssetUploadMethodActivateRequest


def activate_static_asset_upload_method_static_asset_upload_methods_activate_post(
    *,
    body: StaticAssetUploadMethodActivateRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset-upload-methods-activate",
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

from ..models import StaticAssetUploadMethodActivateRequest


def deactivate_static_asset_upload_method_static_asset_upload_methods_deactivate_post(
    *,
    body: StaticAssetUploadMethodActivateRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset-upload-methods-deactivate",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    StaticAssetUploadMethod,
    StaticAssetUploadMethodStateResponse,
)
from ..types import UNSET


@overload
def get_static_asset_upload_method_state_static_asset_upload_method_states__static_asset_upload_method__get(
    static_asset_upload_method: StaticAssetUploadMethod,
    *,
    workspace_uid: int,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_static_asset_upload_method_state_static_asset_upload_method_states__static_asset_upload_method__get(
    static_asset_upload_method: StaticAssetUploadMethod,
    *,
    workspace_uid: int,
    raw: Literal[False] = False,
) -> StaticAssetUploadMethodStateResponse: ...


def get_static_asset_upload_method_state_static_asset_upload_method_states__static_asset_upload_method__get(
    static_asset_upload_method: StaticAssetUploadMethod,
    *,
    workspace_uid: int,
    raw: bool = False,
) -> StaticAssetUploadMethodStateResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/static-asset-upload-method-states/{static_asset_upload_method}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> StaticAssetUploadMethodStateResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as StaticAssetUploadMethodStateResponse
        response_200 = StaticAssetUploadMethodStateResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet,
)


@overload
def list_static_asset_upload_method_state_static_asset_upload_method_states_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_static_asset_upload_method_state_static_asset_upload_method_states_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet: ...


def list_static_asset_upload_method_state_static_asset_upload_method_states_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset-upload-method-states",
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
    ) -> ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet
        response_200 = ListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGetResponseListStaticAssetUploadMethodStateStaticAssetUploadMethodStatesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
