# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DataConnectorStateResponse
from ..types import UNSET


@overload
def get_connector_by_type_v1_connectors__type__get(
    type: str, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_connector_by_type_v1_connectors__type__get(
    type: str, *, workspace_uid: int, raw: Literal[False] = False
) -> DataConnectorStateResponse: ...


def get_connector_by_type_v1_connectors__type__get(
    type: str, *, workspace_uid: int, raw: bool = False
) -> DataConnectorStateResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connectors/{type}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataConnectorStateResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataConnectorStateResponse
        response_200 = DataConnectorStateResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, cast, overload

import requests
from typing_extensions import Literal


@overload
def get_connector_permissions_for_type_v1_connector_permissions__type__get(
    type: str, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_connector_permissions_for_type_v1_connector_permissions__type__get(
    type: str, *, workspace_uid: int, raw: Literal[False] = False
) -> List[str]: ...


def get_connector_permissions_for_type_v1_connector_permissions__type__get(
    type: str, *, workspace_uid: int, raw: bool = False
) -> List[str] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connector-permissions/{type}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List[str]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[str]
        response_200 = cast(List[str], response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet,
)


@overload
def get_connector_type_roles_structured_v1_connectors__type__role_configuration_get(
    type: str, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_connector_type_roles_structured_v1_connectors__type__role_configuration_get(
    type: str, *, workspace_uid: int, raw: Literal[False] = False
) -> GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet: ...


def get_connector_type_roles_structured_v1_connectors__type__role_configuration_get(
    type: str, *, workspace_uid: int, raw: bool = False
) -> (
    GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connectors/{type}/role-configuration",
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
    ) -> GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet
        response_200 = GetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGetResponseGetConnectorTypeRolesStructuredV1ConnectorsTypeRoleConfigurationGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet,
)


@overload
def list_available_connector_types_v1_available_connectors_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_available_connector_types_v1_available_connectors_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet: ...


def list_available_connector_types_v1_available_connectors_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v1/available-connectors",
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
    ) -> ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet
        response_200 = ListAvailableConnectorTypesV1AvailableConnectorsGetResponseListAvailableConnectorTypesV1AvailableConnectorsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet,
)


@overload
def list_connector_permissions_v1_connector_permissions_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_connector_permissions_v1_connector_permissions_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet: ...


def list_connector_permissions_v1_connector_permissions_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v1/connector-permissions",
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
    ) -> ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet
        response_200 = ListConnectorPermissionsV1ConnectorPermissionsGetResponseListConnectorPermissionsV1ConnectorPermissionsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet,
)


@overload
def list_connector_types_v1_connectors_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_connector_types_v1_connectors_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet: ...


def list_connector_types_v1_connectors_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v1/connectors",
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
    ) -> ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet
        response_200 = ListConnectorTypesV1ConnectorsGetResponseListConnectorTypesV1ConnectorsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
