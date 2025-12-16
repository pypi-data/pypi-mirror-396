# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..types import UNSET


@overload
def get_load_config_nodes__node_uid__data_sources_load_config_get(
    node_uid: int, *, split: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_load_config_nodes__node_uid__data_sources_load_config_get(
    node_uid: int, *, split: str, raw: Literal[False] = False
) -> Any: ...


def get_load_config_nodes__node_uid__data_sources_load_config_get(
    node_uid: int, *, split: str, raw: bool = False
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/load-config",
        "params": params,
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


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import TaskDatasourcesResponse
from ..types import Unset


@overload
def list_task_datasources_nodes__node_uid__data_sources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    supports_dev: Union[Unset, bool] = UNSET,
    compute_statistics: Union[Unset, bool] = True,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_task_datasources_nodes__node_uid__data_sources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    supports_dev: Union[Unset, bool] = UNSET,
    compute_statistics: Union[Unset, bool] = True,
    raw: Literal[False] = False,
) -> List["TaskDatasourcesResponse"]: ...


def list_task_datasources_nodes__node_uid__data_sources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    supports_dev: Union[Unset, bool] = UNSET,
    compute_statistics: Union[Unset, bool] = True,
    raw: bool = False,
) -> List["TaskDatasourcesResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["is_active"] = is_active

    params["supports_dev"] = supports_dev

    params["compute_statistics"] = compute_statistics

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["TaskDatasourcesResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['TaskDatasourcesResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = TaskDatasourcesResponse.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import PatchTaskDatasourceParams


def patch_task_datasource_nodes__node_uid__data_sources__datasource_uid__patch(
    node_uid: int,
    datasource_uid: int,
    *,
    body: PatchTaskDatasourceParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/{datasource_uid}",
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

from ..models import TaskDatasourceBulkUpdateParams


def set_task_datasources_active_nodes__node_uid__data_sources_set_active_patch(
    node_uid: int,
    *,
    body: TaskDatasourceBulkUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/set-active",
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

from ..models import TaskDatasourceBulkUpdateParams


def set_task_datasources_inactive_nodes__node_uid__data_sources_set_inactive_patch(
    node_uid: int,
    *,
    body: TaskDatasourceBulkUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/set-inactive",
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

from ..models import TaskDatasourceBulkUpdateParams


def set_task_datasources_no_supports_dev_nodes__node_uid__data_sources_set_no_supports_dev_patch(
    node_uid: int,
    *,
    body: TaskDatasourceBulkUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/set-no-supports-dev",
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

from ..models import TaskDatasourceBulkUpdateParams


def set_task_datasources_supports_dev_nodes__node_uid__data_sources_set_supports_dev_patch(
    node_uid: int,
    *,
    body: TaskDatasourceBulkUpdateParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/data-sources/set-supports-dev",
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
