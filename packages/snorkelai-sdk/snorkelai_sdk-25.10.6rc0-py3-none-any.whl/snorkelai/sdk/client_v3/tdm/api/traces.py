# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import TraceIndex
from ..types import UNSET, Unset


@overload
def get_dataset_trace_indices_dataset__dataset_uid__trace_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    filter_config_str: Union[Unset, str] = UNSET,
    criteria_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_dataset_trace_indices_dataset__dataset_uid__trace_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    filter_config_str: Union[Unset, str] = UNSET,
    criteria_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> List["TraceIndex"]: ...


def get_dataset_trace_indices_dataset__dataset_uid__trace_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    limit: Union[Unset, int] = UNSET,
    filter_config_str: Union[Unset, str] = UNSET,
    criteria_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> List["TraceIndex"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["limit"] = limit

    params["filter_config_str"] = filter_config_str

    params["criteria_uid"] = criteria_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/trace",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["TraceIndex"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['TraceIndex']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = TraceIndex.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from ..models import TraceStepsRequest, TraceStepsResponse


def get_dataset_trace_steps_dataset__dataset_uid__trace_steps_post(
    dataset_uid: int,
    *,
    body: TraceStepsRequest,
) -> TraceStepsResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/dataset/{dataset_uid}/trace/steps",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> TraceStepsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as TraceStepsResponse
        response_200 = TraceStepsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    BodyValidateDatasetTracesTraceValidatePost,
    ValidateDatasetTracesTraceValidatePostResponseValidateDatasetTracesTraceValidatePost,
)
from ..types import UNSET


def validate_dataset_traces_trace_validate_post(
    *,
    body: BodyValidateDatasetTracesTraceValidatePost,
    trace_column: str,
    workspace_uid: int,
) -> (
    ValidateDatasetTracesTraceValidatePostResponseValidateDatasetTracesTraceValidatePost
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["trace_column"] = trace_column

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/trace/validate",
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ValidateDatasetTracesTraceValidatePostResponseValidateDatasetTracesTraceValidatePost:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ValidateDatasetTracesTraceValidatePostResponseValidateDatasetTracesTraceValidatePost
        response_200 = ValidateDatasetTracesTraceValidatePostResponseValidateDatasetTracesTraceValidatePost.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
