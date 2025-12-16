# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import SystemScopedFeature, WorkspaceScopedFeature


def activate_feature_feature__feature__activate_post(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/activate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, cast

from ..models import (
    FeatureAccessRoleCreationRequest,
    WorkspaceScopedFeature,
)


def add_feature_user_role_mapping_feature__feature__role_post(
    feature: WorkspaceScopedFeature,
    *,
    body: FeatureAccessRoleCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/role",
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


from typing import Any, Union

from ..models import SystemScopedFeature, WorkspaceScopedFeature


def deactivate_feature_feature__feature__deactivate_post(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/deactivate",
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

from ..models import WorkspaceScopedFeature


def delete_feature_user_role_mapping_feature__feature__role__mapping_uid__delete(
    feature: WorkspaceScopedFeature,
    mapping_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/role/{mapping_uid}",
    }

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

from ..models import SystemScopedFeature, WorkspaceScopedFeature
from ..types import UNSET


@overload
def has_access_to_feature_feature__feature__access_get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
    *,
    workspace_uid: int,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def has_access_to_feature_feature__feature__access_get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
    *,
    workspace_uid: int,
    raw: Literal[False] = False,
) -> bool: ...


def has_access_to_feature_feature__feature__access_get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
    *,
    workspace_uid: int,
    raw: bool = False,
) -> bool | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/access",
        "params": params,
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import SystemScopedFeature, WorkspaceScopedFeature


@overload
def is_feature_enabled_feature__feature__get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature], raw: Literal[True]
) -> requests.Response: ...


@overload
def is_feature_enabled_feature__feature__get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature],
    raw: Literal[False] = False,
) -> bool: ...


def is_feature_enabled_feature__feature__get(
    feature: Union[SystemScopedFeature, WorkspaceScopedFeature], raw: bool = False
) -> bool | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}",
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


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import FeatureAccessRole, WorkspaceScopedFeature


@overload
def list_feature_user_role_mappings_feature__feature__roles_get(
    feature: WorkspaceScopedFeature, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_feature_user_role_mappings_feature__feature__roles_get(
    feature: WorkspaceScopedFeature, raw: Literal[False] = False
) -> List["FeatureAccessRole"]: ...


def list_feature_user_role_mappings_feature__feature__roles_get(
    feature: WorkspaceScopedFeature, raw: bool = False
) -> List["FeatureAccessRole"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/roles",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["FeatureAccessRole"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['FeatureAccessRole']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = FeatureAccessRole.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    FeatureAccessRoleUpdateParams,
    WorkspaceScopedFeature,
)


def update_feature_user_role_mapping_feature__feature__role__mapping_uid__put(
    feature: WorkspaceScopedFeature,
    mapping_uid: int,
    *,
    body: FeatureAccessRoleUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/feature/{feature}/role/{mapping_uid}",
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
