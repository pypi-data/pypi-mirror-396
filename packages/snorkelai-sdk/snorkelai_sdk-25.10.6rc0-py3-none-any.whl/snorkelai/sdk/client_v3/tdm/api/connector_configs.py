# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DataConnectorConfigCreationRequest


def create_connector_config_v1_connector_configs_post(
    *,
    body: DataConnectorConfigCreationRequest,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v1/connector-configs",
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


from ..types import UNSET


def delete_connector_config_v1_connector_configs__config_uid__delete(
    config_uid: int,
    *,
    workspace_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connector-configs/{config_uid}",
        "params": params,
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


@overload
def get_config_permissions_v1_connector_configs__config_uid__permissions_get(
    config_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_config_permissions_v1_connector_configs__config_uid__permissions_get(
    config_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> List[str]: ...


def get_config_permissions_v1_connector_configs__config_uid__permissions_get(
    config_uid: int, *, workspace_uid: int, raw: bool = False
) -> List[str] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connector-configs/{config_uid}/permissions",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DataConnectorConfig


@overload
def get_connector_config_v1_connector_configs__config_uid__get(
    config_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_connector_config_v1_connector_configs__config_uid__get(
    config_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> DataConnectorConfig: ...


def get_connector_config_v1_connector_configs__config_uid__get(
    config_uid: int, *, workspace_uid: int, raw: bool = False
) -> DataConnectorConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connector-configs/{config_uid}",
        "params": params,
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

from ..models import DataConnectorConfig


@overload
def list_connector_configs_v1_connector_configs_get(
    *, type: str, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_connector_configs_v1_connector_configs_get(
    *, type: str, workspace_uid: int, raw: Literal[False] = False
) -> List["DataConnectorConfig"]: ...


def list_connector_configs_v1_connector_configs_get(
    *, type: str, workspace_uid: int, raw: bool = False
) -> List["DataConnectorConfig"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["type"] = type

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v1/connector-configs",
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


from typing import Any

from ..models import UpdateConfigRequest


def update_connector_config_v1_connector_configs__config_uid__put(
    config_uid: int,
    *,
    body: UpdateConfigRequest,
    workspace_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v1/connector-configs/{config_uid}",
        "params": params,
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
