# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import APIKey, CreateAPIKeyParams


def create_api_key_users__user_uid__api_keys_post(
    user_uid: int,
    *,
    body: CreateAPIKeyParams,
) -> APIKey:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/api-keys",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> APIKey:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as APIKey
        response_201 = APIKey.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_api_key_users__user_uid__api_keys__api_key_uid__delete(
    user_uid: int,
    api_key_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/api-keys/{api_key_uid}",
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

from ..models import TokenPair, ValidateAPIKeyParams


def endpoint_validate_api_key_validate_api_key_post(
    *,
    body: ValidateAPIKeyParams,
) -> TokenPair:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/validate-api-key",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import APIKeyLimited


@overload
def get_api_key_users__user_uid__api_keys__api_key_uid__get(
    user_uid: int, api_key_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_api_key_users__user_uid__api_keys__api_key_uid__get(
    user_uid: int, api_key_uid: int, raw: Literal[False] = False
) -> APIKeyLimited: ...


def get_api_key_users__user_uid__api_keys__api_key_uid__get(
    user_uid: int, api_key_uid: int, raw: bool = False
) -> APIKeyLimited | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/api-keys/{api_key_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> APIKeyLimited:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as APIKeyLimited
        response_200 = APIKeyLimited.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import APIKeyLimited


@overload
def list_api_keys_users__user_uid__api_keys_get(
    user_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_api_keys_users__user_uid__api_keys_get(
    user_uid: int, raw: Literal[False] = False
) -> List["APIKeyLimited"]: ...


def list_api_keys_users__user_uid__api_keys_get(
    user_uid: int, raw: bool = False
) -> List["APIKeyLimited"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/users/{user_uid}/api-keys",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["APIKeyLimited"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['APIKeyLimited']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = APIKeyLimited.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)
