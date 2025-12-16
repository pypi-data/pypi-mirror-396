# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import ResourceType


def activate_resource_roles_rbac_resource_roles__resource_type__activate_post(
    resource_type: ResourceType,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/rbac-resource-roles/{resource_type}/activate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import ResourceType


def deactivate_resource_roles_rbac_resource_roles__resource_type__deactivate_post(
    resource_type: ResourceType,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/rbac-resource-roles/{resource_type}/deactivate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, cast, overload

import requests
from typing_extensions import Literal

from ..models import ResourceType


@overload
def get_rbac_resource_enabled_rbac_resource_roles__resource_type__enabled_get(
    resource_type: ResourceType, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_rbac_resource_enabled_rbac_resource_roles__resource_type__enabled_get(
    resource_type: ResourceType, raw: Literal[False] = False
) -> bool: ...


def get_rbac_resource_enabled_rbac_resource_roles__resource_type__enabled_get(
    resource_type: ResourceType, raw: bool = False
) -> bool | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/rbac-resource-roles/{resource_type}/enabled",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> bool:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as bool
        # Direct parsing for bool
        return cast(bool, response)

    return _parse_response(response)
