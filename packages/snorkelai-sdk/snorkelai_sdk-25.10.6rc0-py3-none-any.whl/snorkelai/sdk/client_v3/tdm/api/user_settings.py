# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DeleteUserSettingsRequest


def delete_user_setting_user_settings_delete(
    *,
    body: DeleteUserSettingsRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/user-settings",
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

from ..models import RawUserSettingsJsons
from ..types import UNSET, Unset


@overload
def get_user_settings_all_user_settings_raw_get(
    *,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_user_settings_all_user_settings_raw_get(
    *,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> RawUserSettingsJsons: ...


def get_user_settings_all_user_settings_raw_get(
    *,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> RawUserSettingsJsons | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["node_uid"] = node_uid

    params["user_uid"] = user_uid

    params["dataset_batch_uid"] = dataset_batch_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/user-settings-raw",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> RawUserSettingsJsons:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RawUserSettingsJsons
        response_200 = RawUserSettingsJsons.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import UserSettingsJson
from ..types import UNSET, Unset


@overload
def get_user_settings_user_settings_get(
    *,
    organization: Union[Unset, bool] = UNSET,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_user_settings_user_settings_get(
    *,
    organization: Union[Unset, bool] = UNSET,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    raw: Literal[False] = False,
) -> UserSettingsJson: ...


def get_user_settings_user_settings_get(
    *,
    organization: Union[Unset, bool] = UNSET,
    node_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    dataset_batch_uid: Union[Unset, int] = UNSET,
    exact: Union[Unset, bool] = UNSET,
    raw: bool = False,
) -> UserSettingsJson | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["organization"] = organization

    params["node_uid"] = node_uid

    params["user_uid"] = user_uid

    params["dataset_batch_uid"] = dataset_batch_uid

    params["exact"] = exact

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/user-settings",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> UserSettingsJson:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserSettingsJson
        response_200 = UserSettingsJson.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateUserSettingsRequest, UserSettingsJson


def update_user_setting_user_settings_post(
    *,
    body: UpdateUserSettingsRequest,
) -> UserSettingsJson:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/user-settings",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UserSettingsJson:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UserSettingsJson
        response_201 = UserSettingsJson.from_dict(response)

        return response_201

    return _parse_response(response)
