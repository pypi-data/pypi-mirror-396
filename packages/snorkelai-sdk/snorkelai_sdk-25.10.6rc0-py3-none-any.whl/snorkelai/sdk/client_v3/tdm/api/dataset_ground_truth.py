# This file is generated from OpenAPI and not meant to be manually edited.
import datetime
from typing import Any, Dict, Union

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import DatasetGroundTruth
from ..types import UNSET, Unset


def create_dataset_ground_truth_dataset__dataset_uid__ground_truth_post(
    dataset_uid: int,
    *,
    label_schema_uid: int,
    x_uid: str,
    committed_by: int,
    label: Any,
    batch_uid: Union[Unset, int] = UNSET,
    source_uid: Union[Unset, int] = UNSET,
    timezone: Union[Unset, str] = UNSET,
    ts: Union[Unset, datetime.datetime] = UNSET,
) -> DatasetGroundTruth:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["label_schema_uid"] = label_schema_uid

    params["x_uid"] = x_uid

    params["committed_by"] = committed_by

    params["label"] = label

    params["batch_uid"] = batch_uid

    params["source_uid"] = source_uid

    params["timezone"] = timezone

    json_ts: Union[Unset, str] = UNSET
    if not isinstance(ts, Unset):
        json_ts = ts.isoformat()
    params["ts"] = json_ts

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/ground-truth",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetGroundTruth:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetGroundTruth
        response_201 = DatasetGroundTruth.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..types import UNSET


def delete_dataset_ground_truth_per_datapoint_dataset__dataset_uid__ground_truth__x_uid__delete(
    dataset_uid: int,
    x_uid: str,
    *,
    label_schema_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["label_schema_uid"] = label_schema_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/ground-truth/{x_uid}",
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


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetGroundTruth
from ..types import UNSET, Unset


@overload
def get_dataset_ground_truth_dataset_ground_truth_get(
    *,
    dataset_uid: int,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted: Union[Unset, bool] = False,
    x_uid: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_dataset_ground_truth_dataset_ground_truth_get(
    *,
    dataset_uid: int,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted: Union[Unset, bool] = False,
    x_uid: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> List["DatasetGroundTruth"]: ...


def get_dataset_ground_truth_dataset_ground_truth_get(
    *,
    dataset_uid: int,
    label_schema_uids: Union[Unset, List[int]] = UNSET,
    user_formatted: Union[Unset, bool] = False,
    x_uid: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> List["DatasetGroundTruth"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["dataset_uid"] = dataset_uid

    json_label_schema_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(label_schema_uids, Unset):
        json_label_schema_uids = label_schema_uids

    params["label_schema_uids"] = json_label_schema_uids

    params["user_formatted"] = user_formatted

    params["x_uid"] = x_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-ground-truth",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetGroundTruth"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetGroundTruth']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetGroundTruth.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    CreateTaskGroundTruthResponse,
    ImportDatasetGroundTruthParams,
)


def import_dataset_ground_truth_dataset__dataset_uid__ingest_ground_truth_post(
    dataset_uid: int,
    *,
    body: ImportDatasetGroundTruthParams,
) -> CreateTaskGroundTruthResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/ingest-ground-truth",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateTaskGroundTruthResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateTaskGroundTruthResponse
        response_201 = CreateTaskGroundTruthResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    GroundTruthGroupBy,
    ListAggregatedSmeFeedbackGroundTruthResponse,
)
from ..types import UNSET, Unset


@overload
def list_aggregated_sme_feedback_ground_truth_dataset__dataset_uid__aggregated_sme_feedback_ground_truth_get(
    dataset_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    workflow_uid: Union[Unset, int] = UNSET,
    group_by: Union[Unset, GroundTruthGroupBy] = UNSET,
    timeout_seconds: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_aggregated_sme_feedback_ground_truth_dataset__dataset_uid__aggregated_sme_feedback_ground_truth_get(
    dataset_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    workflow_uid: Union[Unset, int] = UNSET,
    group_by: Union[Unset, GroundTruthGroupBy] = UNSET,
    timeout_seconds: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> ListAggregatedSmeFeedbackGroundTruthResponse: ...


def list_aggregated_sme_feedback_ground_truth_dataset__dataset_uid__aggregated_sme_feedback_ground_truth_get(
    dataset_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    workflow_uid: Union[Unset, int] = UNSET,
    group_by: Union[Unset, GroundTruthGroupBy] = UNSET,
    timeout_seconds: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> ListAggregatedSmeFeedbackGroundTruthResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    params["workflow_uid"] = workflow_uid

    json_group_by: Union[Unset, str] = UNSET
    if not isinstance(group_by, Unset):
        json_group_by = group_by.value

    params["group_by"] = json_group_by

    params["timeout_seconds"] = timeout_seconds

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/aggregated-sme-feedback-ground-truth",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListAggregatedSmeFeedbackGroundTruthResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListAggregatedSmeFeedbackGroundTruthResponse
        response_201 = ListAggregatedSmeFeedbackGroundTruthResponse.from_dict(response)

        return response_201

    return _parse_response(response)


import datetime
from typing import Any, Union

from ..models import DatasetGroundTruth
from ..types import UNSET, Unset


def update_dataset_ground_truth_per_datapoint_dataset__dataset_uid__ground_truth__x_uid__put(
    dataset_uid: int,
    x_uid: str,
    *,
    label_schema_uid: int,
    label: Union[Unset, str] = UNSET,
    labels: Union[Unset, str] = UNSET,
    batch_uid: Union[Unset, int] = UNSET,
    source_uid: Union[Unset, int] = UNSET,
    timezone: Union[Unset, str] = UNSET,
    ts: Union[Unset, datetime.datetime] = UNSET,
) -> DatasetGroundTruth:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["label_schema_uid"] = label_schema_uid

    params["label"] = label

    params["labels"] = labels

    params["batch_uid"] = batch_uid

    params["source_uid"] = source_uid

    params["timezone"] = timezone

    json_ts: Union[Unset, str] = UNSET
    if not isinstance(ts, Unset):
        json_ts = ts.isoformat()
    params["ts"] = json_ts

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/ground-truth/{x_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DatasetGroundTruth:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasetGroundTruth
        response_201 = DatasetGroundTruth.from_dict(response)

        return response_201

    return _parse_response(response)
