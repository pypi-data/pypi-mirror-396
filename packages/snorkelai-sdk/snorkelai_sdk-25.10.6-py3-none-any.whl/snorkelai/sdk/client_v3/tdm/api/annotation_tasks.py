# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    AddAssigneesToAnnotationTaskParams,
    AddAssigneesToAnnotationTaskResponse,
)


def add_assignees_to_annotation_task_annotation_tasks__annotation_task_uid__assignees_post(
    annotation_task_uid: int,
    *,
    body: AddAssigneesToAnnotationTaskParams,
) -> AddAssigneesToAnnotationTaskResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/assignees",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AddAssigneesToAnnotationTaskResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AddAssigneesToAnnotationTaskResponse
        response_201 = AddAssigneesToAnnotationTaskResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import (
    AddXUidsToAnnotationTaskResponse,
    DataPointSelectionParams,
)


def add_x_uids_to_annotation_task_annotation_tasks__annotation_task_uid__x_uids_post(
    annotation_task_uid: int,
    *,
    body: DataPointSelectionParams,
) -> AddXUidsToAnnotationTaskResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/x_uids",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AddXUidsToAnnotationTaskResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AddXUidsToAnnotationTaskResponse
        response_201 = AddXUidsToAnnotationTaskResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import AnnotationTask, CreateAnnotationTaskParams


def create_annotation_task_datasets__dataset_uid__annotation_tasks_post(
    dataset_uid: int,
    *,
    body: CreateAnnotationTaskParams,
) -> AnnotationTask:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/annotation-tasks",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AnnotationTask:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnnotationTask
        response_201 = AnnotationTask.from_dict(response)

        return response_201

    return _parse_response(response)


def delete_annotation_task_annotation_tasks__annotation_task_uid__delete(
    annotation_task_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}",
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

from ..models import DeleteAssigneesFromAnnotationTaskParams


def delete_assignees_from_annotation_task_annotation_tasks__annotation_task_uid__assignees_delete(
    annotation_task_uid: int,
    *,
    body: DeleteAssigneesFromAnnotationTaskParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/assignees",
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

from ..models import DataPointSelectionParams


def delete_x_uids_from_annotation_task_annotation_tasks__annotation_task_uid__x_uids_delete(
    annotation_task_uid: int,
    *,
    body: DataPointSelectionParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/x_uids",
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import DataFrameResponse
from ..types import UNSET, Unset


@overload
def fetch_annotation_task_dataframes_annotation_tasks__annotation_task_uid__dataframes_get(
    annotation_task_uid: int,
    *,
    dataset_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    include_x_uids: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def fetch_annotation_task_dataframes_annotation_tasks__annotation_task_uid__dataframes_get(
    annotation_task_uid: int,
    *,
    dataset_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    include_x_uids: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> DataFrameResponse: ...


def fetch_annotation_task_dataframes_annotation_tasks__annotation_task_uid__dataframes_get(
    annotation_task_uid: int,
    *,
    dataset_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    include_x_uids: Union[Unset, bool] = False,
    raw: bool = False,
) -> DataFrameResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["limit"] = limit

    params["offset"] = offset

    params["filter_config_str"] = filter_config_str

    params["include_x_uids"] = include_x_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/dataframes",
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


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import LabelSchema


@overload
def fetch_annotation_task_label_schemas_annotation_tasks__annotation_task_uid__label_schemas_get(
    annotation_task_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_annotation_task_label_schemas_annotation_tasks__annotation_task_uid__label_schemas_get(
    annotation_task_uid: int, raw: Literal[False] = False
) -> List["LabelSchema"]: ...


def fetch_annotation_task_label_schemas_annotation_tasks__annotation_task_uid__label_schemas_get(
    annotation_task_uid: int, raw: bool = False
) -> List["LabelSchema"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/label-schemas",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["LabelSchema"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['LabelSchema']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = LabelSchema.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTask


@overload
def get_annotation_task_annotation_tasks__annotation_task_uid__get(
    annotation_task_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_annotation_task_annotation_tasks__annotation_task_uid__get(
    annotation_task_uid: int, raw: Literal[False] = False
) -> AnnotationTask: ...


def get_annotation_task_annotation_tasks__annotation_task_uid__get(
    annotation_task_uid: int, raw: bool = False
) -> AnnotationTask | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AnnotationTask:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnnotationTask
        response_200 = AnnotationTask.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import GetAnnotationTaskAssigneesResponse


@overload
def get_annotation_task_assignees_annotation_tasks__annotation_task_uid__assignees_get(
    annotation_task_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_annotation_task_assignees_annotation_tasks__annotation_task_uid__assignees_get(
    annotation_task_uid: int, raw: Literal[False] = False
) -> GetAnnotationTaskAssigneesResponse: ...


def get_annotation_task_assignees_annotation_tasks__annotation_task_uid__assignees_get(
    annotation_task_uid: int, raw: bool = False
) -> GetAnnotationTaskAssigneesResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/assignees",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetAnnotationTaskAssigneesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAnnotationTaskAssigneesResponse
        response_200 = GetAnnotationTaskAssigneesResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTaskAssignedWorkResponse
from ..types import UNSET, Unset


@overload
def get_annotation_task_assignments_annotation_tasks_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    self_: Union[Unset, bool] = False,
    include_status: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotation_task_assignments_annotation_tasks_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    self_: Union[Unset, bool] = False,
    include_status: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> List["AnnotationTaskAssignedWorkResponse"]: ...


def get_annotation_task_assignments_annotation_tasks_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    self_: Union[Unset, bool] = False,
    include_status: Union[Unset, bool] = False,
    raw: bool = False,
) -> List["AnnotationTaskAssignedWorkResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["limit"] = limit

    params["offset"] = offset

    params["self"] = self_

    params["include_status"] = include_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/annotation-tasks",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["AnnotationTaskAssignedWorkResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['AnnotationTaskAssignedWorkResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = AnnotationTaskAssignedWorkResponse.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTaskDataResponse


@overload
def get_annotation_task_stats_annotation_tasks__annotation_task_uid__stats_get(
    annotation_task_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_annotation_task_stats_annotation_tasks__annotation_task_uid__stats_get(
    annotation_task_uid: int, raw: Literal[False] = False
) -> AnnotationTaskDataResponse: ...


def get_annotation_task_stats_annotation_tasks__annotation_task_uid__stats_get(
    annotation_task_uid: int, raw: bool = False
) -> AnnotationTaskDataResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/stats",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AnnotationTaskDataResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnnotationTaskDataResponse
        response_200 = AnnotationTaskDataResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTask


@overload
def get_annotation_tasks_datasets__dataset_uid__annotation_tasks_get(
    dataset_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_annotation_tasks_datasets__dataset_uid__annotation_tasks_get(
    dataset_uid: int, raw: Literal[False] = False
) -> List["AnnotationTask"]: ...


def get_annotation_tasks_datasets__dataset_uid__annotation_tasks_get(
    dataset_uid: int, raw: bool = False
) -> List["AnnotationTask"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/annotation-tasks",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["AnnotationTask"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['AnnotationTask']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = AnnotationTask.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet,
)
from ..types import UNSET, Unset


@overload
def get_annotator_assignment_metadata_annotation_tasks__annotation_task_uid__datapoint_annotation_status_get(
    annotation_task_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotator_assignment_metadata_annotation_tasks__annotation_task_uid__datapoint_annotation_status_get(
    annotation_task_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[False] = False,
) -> GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet: ...


def get_annotator_assignment_metadata_annotation_tasks__annotation_task_uid__datapoint_annotation_status_get(
    annotation_task_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: bool = False,
) -> (
    GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/datapoint/annotation-status",
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
    ) -> GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet
        response_200 = GetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGetResponseGetAnnotatorAssignmentMetadataAnnotationTasksAnnotationTaskUidDatapointAnnotationStatusGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTaskFilterStructuresResponse


@overload
def get_populated_filters_info_annotation_tasks__annotation_task_uid__populated_filters_info_get(
    annotation_task_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_populated_filters_info_annotation_tasks__annotation_task_uid__populated_filters_info_get(
    annotation_task_uid: int, raw: Literal[False] = False
) -> AnnotationTaskFilterStructuresResponse: ...


def get_populated_filters_info_annotation_tasks__annotation_task_uid__populated_filters_info_get(
    annotation_task_uid: int, raw: bool = False
) -> AnnotationTaskFilterStructuresResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/populated-filters-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AnnotationTaskFilterStructuresResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnnotationTaskFilterStructuresResponse
        response_200 = AnnotationTaskFilterStructuresResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import SubmitAnnotationTaskResponse
from ..types import UNSET


def submit_annotation_task_annotation_tasks__annotation_task_uid__datapoint_annotation_status_patch(
    annotation_task_uid: int,
    *,
    x_uid: str,
) -> SubmitAnnotationTaskResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["x_uid"] = x_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}/datapoint/annotation-status",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SubmitAnnotationTaskResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SubmitAnnotationTaskResponse
        response_201 = SubmitAnnotationTaskResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import AnnotationTask, UpdateAnnotationTaskParams


def update_annotation_task_annotation_tasks__annotation_task_uid__put(
    annotation_task_uid: int,
    *,
    body: UpdateAnnotationTaskParams,
) -> AnnotationTask:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/annotation-tasks/{annotation_task_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AnnotationTask:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnnotationTask
        response_200 = AnnotationTask.from_dict(response)

        return response_200

    return _parse_response(response)
