# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DataConnectorConfigCreationRequest


def create_data_connector_config_data_connector_configs_post(
    *,
    body: DataConnectorConfigCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-configs",
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


def delete_data_connector_config_data_connector_configs__data_connector_config_uid__delete(
    data_connector_config_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-configs/{data_connector_config_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import CRUDAction, DataConnector
from ..types import UNSET


@overload
def get_data_connector_config_data_connector_permissions_data_connector_configs_permissions__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_config_data_connector_permissions_data_connector_configs_permissions__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: Literal[False] = False
) -> List[CRUDAction]: ...


def get_data_connector_config_data_connector_permissions_data_connector_configs_permissions__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: bool = False
) -> List[CRUDAction] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-configs-permissions/{data_connector}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List[CRUDAction]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[CRUDAction]
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = CRUDAction(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import CRUDAction


@overload
def get_data_connector_config_permissions_data_connector_configs__data_connector_config_uid__permissions_get(
    data_connector_config_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_config_permissions_data_connector_configs__data_connector_config_uid__permissions_get(
    data_connector_config_uid: int, raw: Literal[False] = False
) -> List[CRUDAction]: ...


def get_data_connector_config_permissions_data_connector_configs__data_connector_config_uid__permissions_get(
    data_connector_config_uid: int, raw: bool = False
) -> List[CRUDAction] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-configs/{data_connector_config_uid}/permissions",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List[CRUDAction]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[CRUDAction]
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = CRUDAction(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DataConnectorConfig


@overload
def get_data_connector_configuration_data_connector_configs__data_connector_config_uid__get(
    data_connector_config_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_configuration_data_connector_configs__data_connector_config_uid__get(
    data_connector_config_uid: int, raw: Literal[False] = False
) -> DataConnectorConfig: ...


def get_data_connector_configuration_data_connector_configs__data_connector_config_uid__get(
    data_connector_config_uid: int, raw: bool = False
) -> DataConnectorConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-configs/{data_connector_config_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataConnectorConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataConnectorConfig
        response_200 = DataConnectorConfig.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import DataConnector, DataConnectorConfig


@overload
def get_data_connector_configurations_data_connector_configs_get(
    *, data_connector: DataConnector, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_configurations_data_connector_configs_get(
    *, data_connector: DataConnector, workspace_uid: int, raw: Literal[False] = False
) -> List["DataConnectorConfig"]: ...


def get_data_connector_configurations_data_connector_configs_get(
    *, data_connector: DataConnector, workspace_uid: int, raw: bool = False
) -> List["DataConnectorConfig"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_data_connector = data_connector.value
    params["data_connector"] = json_data_connector

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-configs",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DataConnectorConfig"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DataConnectorConfig']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DataConnectorConfig.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet,
)


@overload
def list_data_connector_config_data_connector_permissions_data_connector_configs_permissions_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_data_connector_config_data_connector_permissions_data_connector_configs_permissions_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet: ...


def list_data_connector_config_data_connector_permissions_data_connector_configs_permissions_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-configs-permissions",
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
    ) -> ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet
        response_200 = ListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGetResponseListDataConnectorConfigDataConnectorPermissionsDataConnectorConfigsPermissionsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import DataConnectorConfigUpdateParams


def update_data_connector_config_data_connector_configs__data_connector_config_uid__put(
    data_connector_config_uid: int,
    *,
    body: DataConnectorConfigUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-configs/{data_connector_config_uid}",
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
