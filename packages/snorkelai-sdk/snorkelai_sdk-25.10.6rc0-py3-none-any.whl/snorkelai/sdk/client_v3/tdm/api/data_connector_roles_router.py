# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DataConnectorRoleCreationRequest


def create_data_connector_role_data_connector_roles_post(
    *,
    body: DataConnectorRoleCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-roles",
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


def delete_data_connector_role_data_connector_roles__role_uid__delete(
    role_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-roles/{role_uid}",
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

from ..models import DataConnectorRole


@overload
def get_data_connector_role_data_connector_roles__role_uid__get(
    role_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_role_data_connector_roles__role_uid__get(
    role_uid: int, raw: Literal[False] = False
) -> DataConnectorRole: ...


def get_data_connector_role_data_connector_roles__role_uid__get(
    role_uid: int, raw: bool = False
) -> DataConnectorRole | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-roles/{role_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataConnectorRole:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataConnectorRole
        response_200 = DataConnectorRole.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    DataConnector,
    ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet,
)
from ..types import UNSET, Unset


@overload
def list_data_connector_roles_data_connector_roles_get(
    *, data_connector: Union[Unset, DataConnector] = UNSET, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_data_connector_roles_data_connector_roles_get(
    *, data_connector: Union[Unset, DataConnector] = UNSET, raw: Literal[False] = False
) -> ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet: ...


def list_data_connector_roles_data_connector_roles_get(
    *, data_connector: Union[Unset, DataConnector] = UNSET, raw: bool = False
) -> (
    ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_data_connector: Union[Unset, str] = UNSET
    if not isinstance(data_connector, Unset):
        json_data_connector = data_connector.value

    params["data_connector"] = json_data_connector

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-roles",
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
    ) -> ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet
        response_200 = ListDataConnectorRolesDataConnectorRolesGetResponseListDataConnectorRolesDataConnectorRolesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import DataConnectorRoleUpdateParams


def update_data_connector_role_data_connector_roles__role_uid__put(
    role_uid: int,
    *,
    body: DataConnectorRoleUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-roles/{role_uid}",
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
