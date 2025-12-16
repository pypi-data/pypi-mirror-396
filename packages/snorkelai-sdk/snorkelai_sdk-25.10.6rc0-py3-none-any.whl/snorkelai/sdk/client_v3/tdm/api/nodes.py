# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import NodeJobResponse, SetNodeDataParams


def add_active_datasources_nodes__node_uid__active_datasources_post(
    node_uid: int,
    *,
    body: SetNodeDataParams,
) -> NodeJobResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/active-datasources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> NodeJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as NodeJobResponse
        response_201 = NodeJobResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import UpdateNodePayload, UpdateNodeResponse


def commit_node_route_nodes__node_uid__put(
    node_uid: int,
    *,
    body: UpdateNodePayload,
) -> UpdateNodeResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UpdateNodeResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UpdateNodeResponse
        response_200 = UpdateNodeResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import CreateNodePayload, CreateNodeResponse


def create_dataset_node_datasets__dataset_uid__nodes_post(
    dataset_uid: int,
    *,
    body: CreateNodePayload,
) -> CreateNodeResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/nodes",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateNodeResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateNodeResponse
        response_201 = CreateNodeResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import DeleteNodePreprocessedDatasource


def delete_active_node_datasource_nodes__node_uid__active_datasources_delete(
    node_uid: int,
    *,
    body: DeleteNodePreprocessedDatasource,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/active-datasources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any


def delete_node_nodes__node_uid__delete(
    node_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasourceRole, PreprocessedDatasourceResponse
from ..types import UNSET, Unset


@overload
def get_node_active_datasources_nodes__node_uid__active_datasources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    ds_role: Union[Unset, DatasourceRole] = UNSET,
    compute_staleness: Union[Unset, bool] = False,
    compute_statistics: Union[Unset, bool] = True,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_node_active_datasources_nodes__node_uid__active_datasources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    ds_role: Union[Unset, DatasourceRole] = UNSET,
    compute_staleness: Union[Unset, bool] = False,
    compute_statistics: Union[Unset, bool] = True,
    raw: Literal[False] = False,
) -> List["PreprocessedDatasourceResponse"]: ...


def get_node_active_datasources_nodes__node_uid__active_datasources_get(
    node_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    is_active: Union[Unset, bool] = UNSET,
    ds_role: Union[Unset, DatasourceRole] = UNSET,
    compute_staleness: Union[Unset, bool] = False,
    compute_statistics: Union[Unset, bool] = True,
    raw: bool = False,
) -> List["PreprocessedDatasourceResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["is_active"] = is_active

    json_ds_role: Union[Unset, int] = UNSET
    if not isinstance(ds_role, Unset):
        json_ds_role = ds_role.value

    params["ds_role"] = json_ds_role

    params["compute_staleness"] = compute_staleness

    params["compute_statistics"] = compute_statistics

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/active-datasources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["PreprocessedDatasourceResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['PreprocessedDatasourceResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = PreprocessedDatasourceResponse.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import GetSettingsResponse


@overload
def get_settings_nodes__node_uid__settings_get(
    node_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_settings_nodes__node_uid__settings_get(
    node_uid: int, raw: Literal[False] = False
) -> GetSettingsResponse: ...


def get_settings_nodes__node_uid__settings_get(
    node_uid: int, raw: bool = False
) -> GetSettingsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/settings",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetSettingsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSettingsResponse
        response_200 = GetSettingsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import Node
from ..types import UNSET, Unset


@overload
def list_dataset_nodes_datasets__dataset_uid__nodes_get(
    dataset_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_dataset_nodes_datasets__dataset_uid__nodes_get(
    dataset_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> List["Node"]: ...


def list_dataset_nodes_datasets__dataset_uid__nodes_get(
    dataset_uid: int,
    *,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> List["Node"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/nodes",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Node"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Node']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Node.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import PutNodePreprocessedDatasource


def put_node_datasource_nodes__node_uid__active_datasources__datasource_uid__put(
    node_uid: int,
    datasource_uid: int,
    *,
    body: PutNodePreprocessedDatasource,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/active-datasources/{datasource_uid}",
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

from ..models import NodeJobResponse, RefreshNodeDataParams


def refresh_active_datasources_nodes__node_uid__refresh_post(
    node_uid: int,
    *,
    body: RefreshNodeDataParams,
) -> NodeJobResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/refresh",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> NodeJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as NodeJobResponse
        response_201 = NodeJobResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import PatchNodePayload, PatchNodeResponse


def update_node_nodes__node_uid__patch(
    node_uid: int,
    *,
    body: PatchNodePayload,
) -> PatchNodeResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PatchNodeResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PatchNodeResponse
        response_200 = PatchNodeResponse.from_dict(response)

        return response_200

    return _parse_response(response)
