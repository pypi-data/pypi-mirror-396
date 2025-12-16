# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateDatasetBatchPayload, DatasetBatch


def add_batch_datasets__dataset_uid__batch_post(
    dataset_uid: int,
    *,
    body: CreateDatasetBatchPayload,
) -> List["DatasetBatch"]:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/batch",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetBatch"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetBatch']
        response_201 = []
        _response_201 = response
        for response_201_item_data in _response_201:
            response_201_item = DatasetBatch.from_dict(response_201_item_data)

            response_201.append(response_201_item)

        return response_201

    return _parse_response(response)


from ..models import AssignLabelSchemasToBatchParams


def add_label_schemas_to_batch_dataset_batches__dataset_batch_uid__label_schemas_post(
    dataset_batch_uid: int,
    *,
    body: AssignLabelSchemasToBatchParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/label-schemas",
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

from ..models import (
    CreateBatchWPromptUidRequest,
    CreateBatchWPromptUidResponse,
)


def create_batch_with_prompt_uid_datasets__dataset_uid__engine_driven_batches_post(
    dataset_uid: int,
    *,
    body: CreateBatchWPromptUidRequest,
) -> CreateBatchWPromptUidResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/engine-driven-batches",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateBatchWPromptUidResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateBatchWPromptUidResponse
        response_200 = CreateBatchWPromptUidResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any


def delete_batch_dataset_batches__dataset_batch_uid__delete(
    dataset_batch_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import DeleteDatasetBatchesParams
from ..types import UNSET


def delete_batches_dataset_batches_delete(
    *,
    body: DeleteDatasetBatchesParams,
    dataset_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-batches",
        "params": params,
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


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import Unset


@overload
def export_batches_dataset_batches__dataset_uid__export_batches_get(
    dataset_uid: int,
    *,
    batch_uids: Union[Unset, List[int]] = UNSET,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    selected_fields: Union[Unset, List[str]] = UNSET,
    include_annotations: Union[Unset, bool] = False,
    include_ground_truth: Union[Unset, bool] = False,
    start_index: Union[Unset, int] = 0,
    max_datapoints_to_export: Union[Unset, int] = UNSET,
    max_chars_per_column: Union[Unset, int] = UNSET,
    csv_delimiter: Union[Unset, str] = ",",
    quote_char: Union[Unset, str] = '\\"',
    escape_char: Union[Unset, str] = "\\",
    raw: Literal[True],
) -> requests.Response: ...


@overload
def export_batches_dataset_batches__dataset_uid__export_batches_get(
    dataset_uid: int,
    *,
    batch_uids: Union[Unset, List[int]] = UNSET,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    selected_fields: Union[Unset, List[str]] = UNSET,
    include_annotations: Union[Unset, bool] = False,
    include_ground_truth: Union[Unset, bool] = False,
    start_index: Union[Unset, int] = 0,
    max_datapoints_to_export: Union[Unset, int] = UNSET,
    max_chars_per_column: Union[Unset, int] = UNSET,
    csv_delimiter: Union[Unset, str] = ",",
    quote_char: Union[Unset, str] = '\\"',
    escape_char: Union[Unset, str] = "\\",
    raw: Literal[False] = False,
) -> Any: ...


def export_batches_dataset_batches__dataset_uid__export_batches_get(
    dataset_uid: int,
    *,
    batch_uids: Union[Unset, List[int]] = UNSET,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    selected_fields: Union[Unset, List[str]] = UNSET,
    include_annotations: Union[Unset, bool] = False,
    include_ground_truth: Union[Unset, bool] = False,
    start_index: Union[Unset, int] = 0,
    max_datapoints_to_export: Union[Unset, int] = UNSET,
    max_chars_per_column: Union[Unset, int] = UNSET,
    csv_delimiter: Union[Unset, str] = ",",
    quote_char: Union[Unset, str] = '\\"',
    escape_char: Union[Unset, str] = "\\",
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_batch_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(batch_uids, Unset):
        json_batch_uids = batch_uids

    params["batch_uids"] = json_batch_uids

    json_label_schema_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(label_schema_uids, Unset):
        json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    json_selected_fields: Union[Unset, List[str]] = UNSET
    if not isinstance(selected_fields, Unset):
        json_selected_fields = selected_fields

    params["selected_fields"] = json_selected_fields

    params["include_annotations"] = include_annotations

    params["include_ground_truth"] = include_ground_truth

    params["start_index"] = start_index

    params["max_datapoints_to_export"] = max_datapoints_to_export

    params["max_chars_per_column"] = max_chars_per_column

    params["csv_delimiter"] = csv_delimiter

    params["quote_char"] = quote_char

    params["escape_char"] = escape_char

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_uid}/export-batches",
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

from ..models import BatchDataResponse
from ..types import UNSET, Unset


@overload
def get_batch_data_dataset_batches__dataset_batch_uid__batch_data_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    group_by: Union[Unset, List[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_batch_data_dataset_batches__dataset_batch_uid__batch_data_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    group_by: Union[Unset, List[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> BatchDataResponse: ...


def get_batch_data_dataset_batches__dataset_batch_uid__batch_data_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    group_by: Union[Unset, List[str]] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> BatchDataResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["filter_config"] = filter_config

    params["ascending"] = ascending

    params["limit"] = limit

    json_group_by: Union[Unset, List[str]] = UNSET
    if not isinstance(group_by, Unset):
        json_group_by = group_by

    params["group_by"] = json_group_by

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/batch-data",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BatchDataResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BatchDataResponse
        response_200 = BatchDataResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import BatchDataResponse
from ..types import UNSET, Unset


@overload
def get_batch_data_docs_dataset_batches__dataset_batch_uid__batch_data_docs_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_batch_data_docs_dataset_batches__dataset_batch_uid__batch_data_docs_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> BatchDataResponse: ...


def get_batch_data_docs_dataset_batches__dataset_batch_uid__batch_data_docs_get(
    dataset_batch_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> BatchDataResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["filter_config"] = filter_config

    params["ascending"] = ascending

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/batch-data/docs",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BatchDataResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BatchDataResponse
        response_200 = BatchDataResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import BatchDataResponse
from ..types import UNSET, Unset


@overload
def get_batch_data_pages_dataset_batches__dataset_batch_uid__batch_data_docs__context_uid__pages_get(
    dataset_batch_uid: int,
    context_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_batch_data_pages_dataset_batches__dataset_batch_uid__batch_data_docs__context_uid__pages_get(
    dataset_batch_uid: int,
    context_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> BatchDataResponse: ...


def get_batch_data_pages_dataset_batches__dataset_batch_uid__batch_data_docs__context_uid__pages_get(
    dataset_batch_uid: int,
    context_uid: int,
    *,
    filter_config: Union[Unset, str] = UNSET,
    ascending: Union[Unset, bool] = True,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> BatchDataResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["filter_config"] = filter_config

    params["ascending"] = ascending

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/batch-data/docs/{context_uid}/pages",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BatchDataResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BatchDataResponse
        response_200 = BatchDataResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal


@overload
def get_batch_dataset_batches__dataset_batch_uid__get(
    dataset_batch_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_batch_dataset_batches__dataset_batch_uid__get(
    dataset_batch_uid: int, raw: Literal[False] = False
) -> DatasetBatch: ...


def get_batch_dataset_batches__dataset_batch_uid__get(
    dataset_batch_uid: int, raw: bool = False
) -> DatasetBatch | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetBatch:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetBatch
        response_200 = DatasetBatch.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import DatasetBatchXUIDResponse


@overload
def get_batch_x_uids_dataset_batches__dataset_batch_uid__x_uids_get(
    dataset_batch_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_batch_x_uids_dataset_batches__dataset_batch_uid__x_uids_get(
    dataset_batch_uid: int, raw: Literal[False] = False
) -> DatasetBatchXUIDResponse: ...


def get_batch_x_uids_dataset_batches__dataset_batch_uid__x_uids_get(
    dataset_batch_uid: int, raw: bool = False
) -> DatasetBatchXUIDResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/x-uids",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetBatchXUIDResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetBatchXUIDResponse
        response_200 = DatasetBatchXUIDResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetBatch
from ..types import UNSET, Unset


@overload
def get_batches_for_dataset_datasets__dataset_uid__batches_get(
    dataset_uid: int, *, user_uid: Union[Unset, int] = UNSET, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_batches_for_dataset_datasets__dataset_uid__batches_get(
    dataset_uid: int,
    *,
    user_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> List["DatasetBatch"]: ...


def get_batches_for_dataset_datasets__dataset_uid__batches_get(
    dataset_uid: int, *, user_uid: Union[Unset, int] = UNSET, raw: bool = False
) -> List["DatasetBatch"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["user_uid"] = user_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/batches",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetBatch"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetBatch']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetBatch.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetBatch
from ..types import UNSET, Unset


@overload
def get_dataset_batches_dataset_batches_get(
    *,
    dataset_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    assignee_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_dataset_batches_dataset_batches_get(
    *,
    dataset_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    assignee_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> List["DatasetBatch"]: ...


def get_dataset_batches_dataset_batches_get(
    *,
    dataset_uid: Union[Unset, int] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    assignee_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> List["DatasetBatch"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["user_uid"] = user_uid

    params["workspace_uid"] = workspace_uid

    params["assignee_uid"] = assignee_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-batches",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetBatch"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetBatch']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetBatch.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import BatchFilterStructuresResponse


@overload
def get_populated_filters_info_dataset_batches__dataset_batch_uid__populated_filters_info_get(
    dataset_batch_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_populated_filters_info_dataset_batches__dataset_batch_uid__populated_filters_info_get(
    dataset_batch_uid: int, raw: Literal[False] = False
) -> BatchFilterStructuresResponse: ...


def get_populated_filters_info_dataset_batches__dataset_batch_uid__populated_filters_info_get(
    dataset_batch_uid: int, raw: bool = False
) -> BatchFilterStructuresResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}/populated-filters-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> BatchFilterStructuresResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as BatchFilterStructuresResponse
        response_200 = BatchFilterStructuresResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import GetSourceSizeResponse
from ..types import UNSET, Unset


@overload
def get_source_size_from_dataset_dataset__dataset_uid__batches_source_size_get(
    dataset_uid: int,
    *,
    source_type: Union[Unset, str] = UNSET,
    source_uid: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_source_size_from_dataset_dataset__dataset_uid__batches_source_size_get(
    dataset_uid: int,
    *,
    source_type: Union[Unset, str] = UNSET,
    source_uid: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> GetSourceSizeResponse: ...


def get_source_size_from_dataset_dataset__dataset_uid__batches_source_size_get(
    dataset_uid: int,
    *,
    source_type: Union[Unset, str] = UNSET,
    source_uid: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> GetSourceSizeResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["source_type"] = source_type

    params["source_uid"] = source_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/batches-source-size",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetSourceSizeResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSourceSizeResponse
        response_200 = GetSourceSizeResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import DatasetBatch, UpdateDatasetBatchParams


def update_batch_dataset_batches__dataset_batch_uid__put(
    dataset_batch_uid: int,
    *,
    body: UpdateDatasetBatchParams,
) -> DatasetBatch:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset-batches/{dataset_batch_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetBatch:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetBatch
        response_200 = DatasetBatch.from_dict(response)

        return response_200

    return _parse_response(response)
