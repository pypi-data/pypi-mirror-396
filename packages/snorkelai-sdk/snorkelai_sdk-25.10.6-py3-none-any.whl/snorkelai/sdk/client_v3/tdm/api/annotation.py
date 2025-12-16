# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    CreateDatasetAnnotationParams,
    CreateDatasetAnnotationResponse,
)


def add_annotation_dataset_annotation_post(
    *,
    body: CreateDatasetAnnotationParams,
) -> CreateDatasetAnnotationResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotation",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateDatasetAnnotationResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateDatasetAnnotationResponse
        response_201 = CreateDatasetAnnotationResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import AggregateDatasetAnnotationsParams


def aggregate_annotations_aggregate_dataset_annotations_post(
    *,
    body: AggregateDatasetAnnotationsParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/aggregate/dataset-annotations",
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


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import GetAnnotationsByXUidResponse
from ..types import UNSET


@overload
def aggregate_annotations_by_x_uid_aggregate_dataset_annotations_get(
    *, dataset_uid: int, x_uid: str, label_schema_uids: List[int], raw: Literal[True]
) -> requests.Response: ...


@overload
def aggregate_annotations_by_x_uid_aggregate_dataset_annotations_get(
    *,
    dataset_uid: int,
    x_uid: str,
    label_schema_uids: List[int],
    raw: Literal[False] = False,
) -> GetAnnotationsByXUidResponse: ...


def aggregate_annotations_by_x_uid_aggregate_dataset_annotations_get(
    *, dataset_uid: int, x_uid: str, label_schema_uids: List[int], raw: bool = False
) -> GetAnnotationsByXUidResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["x_uid"] = x_uid

    json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/aggregate/dataset-annotations",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetAnnotationsByXUidResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAnnotationsByXUidResponse
        response_200 = GetAnnotationsByXUidResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import CommitDatasetAnnotationParams


def commit_annotation_commit_dataset_annotation_post(
    *,
    body: CommitDatasetAnnotationParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/commit/dataset-annotation",
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

from ..models import DeleteDatasetAnnotationParams


def delete_annotation_dataset_annotation_delete(
    *,
    body: DeleteDatasetAnnotationParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotation",
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

from ..models import DeleteDatasetAnnotationsParams


def delete_annotations_dataset_annotations_delete(
    *,
    body: DeleteDatasetAnnotationsParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotations",
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

from ..models import GetAnnotationRateResponse
from ..types import Unset


@overload
def get_annotation_rate_annotations_rate_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    unit: str,
    last: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotation_rate_annotations_rate_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    unit: str,
    last: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[False] = False,
) -> GetAnnotationRateResponse: ...


def get_annotation_rate_annotations_rate_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    unit: str,
    last: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: bool = False,
) -> GetAnnotationRateResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["label_schema_uid"] = label_schema_uid

    params["unit"] = unit

    params["last"] = last

    json_user_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(user_uids, Unset):
        json_user_uids = user_uids

    params["user_uids"] = json_user_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/annotations-rate",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetAnnotationRateResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAnnotationRateResponse
        response_200 = GetAnnotationRateResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import GetAnnotationReviewStatusResponse
from ..types import UNSET, Unset


@overload
def get_annotation_review_status_dataset_annotation_review_status_get(
    *,
    dataset_uid: int,
    x_uid: str,
    label_schema_uids: List[int],
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotation_review_status_dataset_annotation_review_status_get(
    *,
    dataset_uid: int,
    x_uid: str,
    label_schema_uids: List[int],
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[False] = False,
) -> GetAnnotationReviewStatusResponse: ...


def get_annotation_review_status_dataset_annotation_review_status_get(
    *,
    dataset_uid: int,
    x_uid: str,
    label_schema_uids: List[int],
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: bool = False,
) -> GetAnnotationReviewStatusResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["x_uid"] = x_uid

    json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    json_user_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(user_uids, Unset):
        json_user_uids = user_uids

    params["user_uids"] = json_user_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotation/review-status",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetAnnotationReviewStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAnnotationReviewStatusResponse
        response_200 = GetAnnotationReviewStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    GetDatasetAnnotationsResponse,
    SupportedSortColumns,
)
from ..types import UNSET, Unset


@overload
def get_annotations_dataset_annotations_get(
    *,
    dataset_uid: int,
    user_uid: Union[Unset, int] = UNSET,
    user_uids: Union[Unset, List[int]] = UNSET,
    x_uids: Union[Unset, List[str]] = UNSET,
    label: Union[Unset, Any] = UNSET,
    source_uid: Union[Unset, int] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    annotation_task_uids: Union[Unset, List[int]] = UNSET,
    include_batch_metadata: Union[Unset, bool] = False,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted_label: Union[Unset, bool] = False,
    sort_column: Union[Unset, SupportedSortColumns] = UNSET,
    ascending: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotations_dataset_annotations_get(
    *,
    dataset_uid: int,
    user_uid: Union[Unset, int] = UNSET,
    user_uids: Union[Unset, List[int]] = UNSET,
    x_uids: Union[Unset, List[str]] = UNSET,
    label: Union[Unset, Any] = UNSET,
    source_uid: Union[Unset, int] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    annotation_task_uids: Union[Unset, List[int]] = UNSET,
    include_batch_metadata: Union[Unset, bool] = False,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted_label: Union[Unset, bool] = False,
    sort_column: Union[Unset, SupportedSortColumns] = UNSET,
    ascending: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> GetDatasetAnnotationsResponse: ...


def get_annotations_dataset_annotations_get(
    *,
    dataset_uid: int,
    user_uid: Union[Unset, int] = UNSET,
    user_uids: Union[Unset, List[int]] = UNSET,
    x_uids: Union[Unset, List[str]] = UNSET,
    label: Union[Unset, Any] = UNSET,
    source_uid: Union[Unset, int] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    annotation_task_uids: Union[Unset, List[int]] = UNSET,
    include_batch_metadata: Union[Unset, bool] = False,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted_label: Union[Unset, bool] = False,
    sort_column: Union[Unset, SupportedSortColumns] = UNSET,
    ascending: Union[Unset, bool] = False,
    raw: bool = False,
) -> GetDatasetAnnotationsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["user_uid"] = user_uid

    json_user_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(user_uids, Unset):
        json_user_uids = user_uids

    params["user_uids"] = json_user_uids

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    params["label"] = label

    params["source_uid"] = source_uid

    json_batch_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(batch_uids, Unset):
        json_batch_uids = batch_uids

    params["batch_uids"] = json_batch_uids

    json_annotation_task_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(annotation_task_uids, Unset):
        json_annotation_task_uids = annotation_task_uids

    params["annotation_task_uids"] = json_annotation_task_uids

    params["include_batch_metadata"] = include_batch_metadata

    json_label_schema_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(label_schema_uids, Unset):
        json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    params["user_formatted_label"] = user_formatted_label

    json_sort_column: Union[Unset, str] = UNSET
    if not isinstance(sort_column, Unset):
        json_sort_column = sort_column.value

    params["sort_column"] = json_sort_column

    params["ascending"] = ascending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotations",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetDatasetAnnotationsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetDatasetAnnotationsResponse
        response_200 = GetDatasetAnnotationsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetAnnotationsOverviewResponse
from ..types import UNSET, Unset


@overload
def get_annotations_overview_annotations_overview_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_annotations_overview_annotations_overview_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[False] = False,
) -> DatasetAnnotationsOverviewResponse: ...


def get_annotations_overview_annotations_overview_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    raw: bool = False,
) -> DatasetAnnotationsOverviewResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["label_schema_uid"] = label_schema_uid

    json_user_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(user_uids, Unset):
        json_user_uids = user_uids

    params["user_uids"] = json_user_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/annotations-overview",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetAnnotationsOverviewResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetAnnotationsOverviewResponse
        response_200 = DatasetAnnotationsOverviewResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import InterAnnotatorAgreement
from ..types import UNSET, Unset


@overload
def get_interannotator_agreement_annotator_agreement_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    class_value: Union[Unset, int] = UNSET,
    metric: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_interannotator_agreement_annotator_agreement_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    class_value: Union[Unset, int] = UNSET,
    metric: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> InterAnnotatorAgreement: ...


def get_interannotator_agreement_annotator_agreement_get(
    *,
    dataset_uid: int,
    label_schema_uid: int,
    user_uids: Union[Unset, List[int]] = UNSET,
    batch_uids: Union[Unset, List[int]] = UNSET,
    class_value: Union[Unset, int] = UNSET,
    metric: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> InterAnnotatorAgreement | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    params["label_schema_uid"] = label_schema_uid

    json_user_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(user_uids, Unset):
        json_user_uids = user_uids

    params["user_uids"] = json_user_uids

    json_batch_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(batch_uids, Unset):
        json_batch_uids = batch_uids

    params["batch_uids"] = json_batch_uids

    params["class_value"] = class_value

    params["metric"] = metric

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/annotator-agreement",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> InterAnnotatorAgreement:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as InterAnnotatorAgreement
        response_200 = InterAnnotatorAgreement.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    ImportDatasetAnnotationsParams,
    ImportDatasetAnnotationsResponse,
)


def import_annotations_dataset_annotations_post(
    *,
    body: ImportDatasetAnnotationsParams,
) -> ImportDatasetAnnotationsResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotations",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ImportDatasetAnnotationsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ImportDatasetAnnotationsResponse
        response_201 = ImportDatasetAnnotationsResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import UpdateDatasetAnnotationParams


def update_annotation_dataset_annotation_put(
    *,
    body: UpdateDatasetAnnotationParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotation",
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

from ..models import UpdateAnnotationReviewStatusParams


def update_annotation_review_status_dataset_annotation_review_status_patch(
    *,
    body: UpdateAnnotationReviewStatusParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-annotation/review-status",
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
