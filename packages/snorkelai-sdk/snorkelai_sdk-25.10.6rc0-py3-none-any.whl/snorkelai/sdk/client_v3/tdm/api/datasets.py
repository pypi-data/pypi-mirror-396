# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import BaseDataset, DatasetResponse
from ..types import UNSET, Unset


def create_dataset(
    *,
    body: BaseDataset,
    enable_mta: Union[Unset, bool] = False,
    data_type: Union[Unset, str] = UNSET,
) -> DatasetResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["enable_mta"] = enable_mta

    params["data_type"] = data_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/datasets",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetResponse
        response_201 = DatasetResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import RemoveDatasetRequest, RemoveDatasetResponse


def delete_dataset(
    dataset_uid: int,
    *,
    body: RemoveDatasetRequest,
) -> RemoveDatasetResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> RemoveDatasetResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RemoveDatasetResponse
        response_202 = RemoveDatasetResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from ..models import UpdateDatasetParams


def edit_dataset(
    dataset_uid: int,
    *,
    body: UpdateDatasetParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DatasetResponse


@overload
def fetch_dataset_by_uid_datasets__dataset_uid__get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_dataset_by_uid_datasets__dataset_uid__get(
    dataset_uid: int, raw: Literal[False] = False
) -> DatasetResponse: ...


def fetch_dataset_by_uid_datasets__dataset_uid__get(
    dataset_uid: int, raw: bool = False
) -> DatasetResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetResponse
        response_200 = DatasetResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import FetchDatasetColumnTypesResponse
from ..types import UNSET, Unset


@overload
def fetch_dataset_column_types_datasets__dataset_uid__dataframe_column_types_get(
    dataset_uid: int, *, intersection: Union[Unset, bool] = True, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_dataset_column_types_datasets__dataset_uid__dataframe_column_types_get(
    dataset_uid: int,
    *,
    intersection: Union[Unset, bool] = True,
    raw: Literal[False] = False,
) -> FetchDatasetColumnTypesResponse: ...


def fetch_dataset_column_types_datasets__dataset_uid__dataframe_column_types_get(
    dataset_uid: int, *, intersection: Union[Unset, bool] = True, raw: bool = False
) -> FetchDatasetColumnTypesResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["intersection"] = intersection

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/dataframe-column-types",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> FetchDatasetColumnTypesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as FetchDatasetColumnTypesResponse
        response_200 = FetchDatasetColumnTypesResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def fetch_dataset_columns_datasets__dataset_uid__dataframe_columns_get(
    dataset_uid: int,
    *,
    intersection: Union[Unset, bool] = True,
    use_preprocessed_dataset: Union[Unset, bool] = True,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def fetch_dataset_columns_datasets__dataset_uid__dataframe_columns_get(
    dataset_uid: int,
    *,
    intersection: Union[Unset, bool] = True,
    use_preprocessed_dataset: Union[Unset, bool] = True,
    raw: Literal[False] = False,
) -> Any: ...


def fetch_dataset_columns_datasets__dataset_uid__dataframe_columns_get(
    dataset_uid: int,
    *,
    intersection: Union[Unset, bool] = True,
    use_preprocessed_dataset: Union[Unset, bool] = True,
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["intersection"] = intersection

    params["use_preprocessed_dataset"] = use_preprocessed_dataset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/dataframe-columns",
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import DataFrameResponse
from ..types import UNSET, Unset


@overload
def fetch_dataset_dataframes_datasets__dataset_uid__dataframes_get(
    dataset_uid: int,
    *,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    datasource_uid: Union[Unset, int] = UNSET,
    include_slice_membership: Union[Unset, bool] = False,
    include_annotation_task_data: Union[Unset, bool] = False,
    include_x_uids: Union[Unset, bool] = False,
    streaming: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def fetch_dataset_dataframes_datasets__dataset_uid__dataframes_get(
    dataset_uid: int,
    *,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    datasource_uid: Union[Unset, int] = UNSET,
    include_slice_membership: Union[Unset, bool] = False,
    include_annotation_task_data: Union[Unset, bool] = False,
    include_x_uids: Union[Unset, bool] = False,
    streaming: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> DataFrameResponse: ...


def fetch_dataset_dataframes_datasets__dataset_uid__dataframes_get(
    dataset_uid: int,
    *,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    split: Union[Unset, str] = UNSET,
    datasource_uid: Union[Unset, int] = UNSET,
    include_slice_membership: Union[Unset, bool] = False,
    include_annotation_task_data: Union[Unset, bool] = False,
    include_x_uids: Union[Unset, bool] = False,
    streaming: Union[Unset, bool] = False,
    raw: bool = False,
) -> DataFrameResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["virtualized_dataset_uid"] = virtualized_dataset_uid

    params["limit"] = limit

    params["offset"] = offset

    params["filter_config_str"] = filter_config_str

    params["split"] = split

    params["datasource_uid"] = datasource_uid

    params["include_slice_membership"] = include_slice_membership

    params["include_annotation_task_data"] = include_annotation_task_data

    params["include_x_uids"] = include_x_uids

    params["streaming"] = streaming

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/dataframes",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataFrameResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataFrameResponse
        response_200 = DataFrameResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    GarbageCollectDatasetApplicationParams,
    RemoveDatasetResponse,
)


def garbage_collect_dataset_applications(
    *,
    body: GarbageCollectDatasetApplicationParams,
) -> RemoveDatasetResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/datasets",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> RemoveDatasetResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RemoveDatasetResponse
        response_202 = RemoveDatasetResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import ListDatasetsResponse
from ..types import UNSET, Unset


@overload
def get_datasets(
    *,
    name: Union[Unset, str] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    exclude_non_arrow_datasets: Union[Unset, bool] = False,
    next_cursor: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_datasets(
    *,
    name: Union[Unset, str] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    exclude_non_arrow_datasets: Union[Unset, bool] = False,
    next_cursor: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> List["ListDatasetsResponse"]: ...


def get_datasets(
    *,
    name: Union[Unset, str] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    exclude_non_arrow_datasets: Union[Unset, bool] = False,
    next_cursor: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> List["ListDatasetsResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["name"] = name

    params["workspace_uid"] = workspace_uid

    params["exclude_non_arrow_datasets"] = exclude_non_arrow_datasets

    params["next_cursor"] = next_cursor

    params["limit"] = limit

    params["offset"] = offset

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/datasets",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["ListDatasetsResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['ListDatasetsResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = ListDatasetsResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DatasetFilterStructuresResponse


@overload
def get_populated_filters_info_datasets__dataset_uid__populated_filters_info_get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_populated_filters_info_datasets__dataset_uid__populated_filters_info_get(
    dataset_uid: int, raw: Literal[False] = False
) -> DatasetFilterStructuresResponse: ...


def get_populated_filters_info_datasets__dataset_uid__populated_filters_info_get(
    dataset_uid: int, raw: bool = False
) -> DatasetFilterStructuresResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/populated-filters-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetFilterStructuresResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetFilterStructuresResponse
        response_200 = DatasetFilterStructuresResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, cast, overload

import requests
from typing_extensions import Literal


@overload
def list_dataset_data_splits_datasets__dataset_uid__splits_get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_dataset_data_splits_datasets__dataset_uid__splits_get(
    dataset_uid: int, raw: Literal[False] = False
) -> List[str]: ...


def list_dataset_data_splits_datasets__dataset_uid__splits_get(
    dataset_uid: int, raw: bool = False
) -> List[str] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/splits",
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
