# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateWorkspacePayload,
    CreateWorkspaceResponse,
)


def create_workspace_workspaces_post(
    *,
    body: CreateWorkspacePayload,
) -> CreateWorkspaceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workspaces",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateWorkspaceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateWorkspaceResponse
        response_201 = CreateWorkspaceResponse.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_workspaces__workspace_uid__delete(
    workspace_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspaces/{workspace_uid}",
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

from ..models import WorkspaceSettings


@overload
def get_workspace_settings_workspace_settings_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_workspace_settings_workspace_settings_get(
    raw: Literal[False] = False,
) -> WorkspaceSettings: ...


def get_workspace_settings_workspace_settings_get(
    raw: bool = False,
) -> WorkspaceSettings | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workspace-settings",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> WorkspaceSettings:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as WorkspaceSettings
        response_200 = WorkspaceSettings.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import GetWorkspaceResponse


@overload
def get_workspace_workspaces__workspace_uid__get(
    workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workspace_workspaces__workspace_uid__get(
    workspace_uid: int, raw: Literal[False] = False
) -> GetWorkspaceResponse: ...


def get_workspace_workspaces__workspace_uid__get(
    workspace_uid: int, raw: bool = False
) -> GetWorkspaceResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspaces/{workspace_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetWorkspaceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetWorkspaceResponse
        response_200 = GetWorkspaceResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import ListWorkspaceResponse, UserRole
from ..types import UNSET, Unset


@overload
def list_workspaces_workspaces_get(
    *,
    workspace_name: Union[Unset, str] = UNSET,
    roles: Union[Unset, List[UserRole]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_workspaces_workspaces_get(
    *,
    workspace_name: Union[Unset, str] = UNSET,
    roles: Union[Unset, List[UserRole]] = UNSET,
    raw: Literal[False] = False,
) -> ListWorkspaceResponse: ...


def list_workspaces_workspaces_get(
    *,
    workspace_name: Union[Unset, str] = UNSET,
    roles: Union[Unset, List[UserRole]] = UNSET,
    raw: bool = False,
) -> ListWorkspaceResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_name"] = workspace_name

    json_roles: Union[Unset, List[str]] = UNSET
    if not isinstance(roles, Unset):
        json_roles = []
        for roles_item_data in roles:
            roles_item = roles_item_data.value
            json_roles.append(roles_item)

    params["roles"] = json_roles

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workspaces",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListWorkspaceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListWorkspaceResponse
        response_200 = ListWorkspaceResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import PatchWorkspaceRolesPayload


def patch_workspace_roles_workspaces__workspace_uid__roles_patch(
    workspace_uid: int,
    *,
    body: PatchWorkspaceRolesPayload,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspaces/{workspace_uid}/roles",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import PutWorkspacePayload


def put_workspace_workspaces__workspace_uid__put(
    workspace_uid: int,
    *,
    body: PutWorkspacePayload,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspaces/{workspace_uid}",
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

from ..models import WorkspaceSettings


def update_workspace_settings_workspace_settings_put(
    *,
    body: WorkspaceSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workspace-settings",
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
