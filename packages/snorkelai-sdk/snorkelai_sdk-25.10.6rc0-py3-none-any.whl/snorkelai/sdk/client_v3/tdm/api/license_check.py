# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import InstanceInformation


@overload
def get_instance_information_license_instance_info_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_instance_information_license_instance_info_get(
    raw: Literal[False] = False,
) -> InstanceInformation: ...


def get_instance_information_license_instance_info_get(
    raw: bool = False,
) -> InstanceInformation | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/license/instance-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> InstanceInformation:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as InstanceInformation
        response_200 = InstanceInformation.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal


@overload
def get_license_info_license_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_license_info_license_get(raw: Literal[False] = False) -> Any: ...


def get_license_info_license_get(raw: bool = False) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/license",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal


@overload
def get_system_key_license_system_validation_key_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_system_key_license_system_validation_key_get(
    raw: Literal[False] = False,
) -> Any: ...


def get_system_key_license_system_validation_key_get(
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/license/system-validation-key",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import LicenseKey


def put_license_license_put(
    *,
    body: LicenseKey,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/license",
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


from typing import Any, overload

import requests
from typing_extensions import Literal


@overload
def validate_license_license_validate_get(raw: Literal[True]) -> requests.Response: ...


@overload
def validate_license_license_validate_get(raw: Literal[False] = False) -> Any: ...


def validate_license_license_validate_get(raw: bool = False) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/license/validate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
