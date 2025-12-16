# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DataConnectorActivateRequest


def activate_data_connector_data_connectors_activate_post(
    *,
    body: DataConnectorActivateRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connectors-activate",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import DataConnectorActivateRequest


def deactivate_data_connector_data_connectors_deactivate_post(
    *,
    body: DataConnectorActivateRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connectors-deactivate",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DataConnector, DataConnectorStateResponse
from ..types import UNSET


@overload
def get_data_connector_state_data_connector_states__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_data_connector_state_data_connector_states__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: Literal[False] = False
) -> DataConnectorStateResponse: ...


def get_data_connector_state_data_connector_states__data_connector__get(
    data_connector: DataConnector, *, workspace_uid: int, raw: bool = False
) -> DataConnectorStateResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-connector-states/{data_connector}",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet,
)


@overload
def list_data_connector_state_data_connector_states_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_data_connector_state_data_connector_states_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet: ...


def list_data_connector_state_data_connector_states_get(
    *, workspace_uid: int, raw: bool = False
) -> (
    ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-connector-states",
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
    ) -> ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet
        response_200 = ListDataConnectorStateDataConnectorStatesGetResponseListDataConnectorStateDataConnectorStatesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
