# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


def cancel_job_jobs__job_uid__cancel_post(
    job_uid: str,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/jobs/{job_uid}/cancel",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any


def delete_job_jobs__job_uid__delete_post(
    job_uid: str,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/jobs/{job_uid}/delete",
    }

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

from ..models import JobInfo


@overload
def get_job_for_uid_jobs__job_uid__get(
    job_uid: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_job_for_uid_jobs__job_uid__get(
    job_uid: str, raw: Literal[False] = False
) -> JobInfo: ...


def get_job_for_uid_jobs__job_uid__get(
    job_uid: str, raw: bool = False
) -> JobInfo | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/jobs/{job_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> JobInfo:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as JobInfo
        response_200 = JobInfo.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    JobListResponse,
    JobSourceEnum,
    JobState,
    JobType,
)
from ..types import UNSET, Unset


@overload
def list_jobs_jobs_get(
    *,
    job_source: Union[Unset, JobSourceEnum] = UNSET,
    job_type: Union[Unset, JobType] = UNSET,
    dataset_id: Union[Unset, int] = UNSET,
    node_id: Union[Unset, int] = UNSET,
    workspace_id: Union[Unset, int] = UNSET,
    state: Union[Unset, JobState] = UNSET,
    start_time: Union[Unset, float] = UNSET,
    direction: Union[Unset, str] = "older",
    limit: Union[Unset, int] = 100,
    details: Union[Unset, bool] = False,
    user_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_jobs_jobs_get(
    *,
    job_source: Union[Unset, JobSourceEnum] = UNSET,
    job_type: Union[Unset, JobType] = UNSET,
    dataset_id: Union[Unset, int] = UNSET,
    node_id: Union[Unset, int] = UNSET,
    workspace_id: Union[Unset, int] = UNSET,
    state: Union[Unset, JobState] = UNSET,
    start_time: Union[Unset, float] = UNSET,
    direction: Union[Unset, str] = "older",
    limit: Union[Unset, int] = 100,
    details: Union[Unset, bool] = False,
    user_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> JobListResponse: ...


def list_jobs_jobs_get(
    *,
    job_source: Union[Unset, JobSourceEnum] = UNSET,
    job_type: Union[Unset, JobType] = UNSET,
    dataset_id: Union[Unset, int] = UNSET,
    node_id: Union[Unset, int] = UNSET,
    workspace_id: Union[Unset, int] = UNSET,
    state: Union[Unset, JobState] = UNSET,
    start_time: Union[Unset, float] = UNSET,
    direction: Union[Unset, str] = "older",
    limit: Union[Unset, int] = 100,
    details: Union[Unset, bool] = False,
    user_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> JobListResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_job_source: Union[Unset, str] = UNSET
    if not isinstance(job_source, Unset):
        json_job_source = job_source.value

    params["job_source"] = json_job_source

    json_job_type: Union[Unset, str] = UNSET
    if not isinstance(job_type, Unset):
        json_job_type = job_type.value

    params["job_type"] = json_job_type

    params["dataset_id"] = dataset_id

    params["node_id"] = node_id

    params["workspace_id"] = workspace_id

    json_state: Union[Unset, str] = UNSET
    if not isinstance(state, Unset):
        json_state = state.value

    params["state"] = json_state

    params["start_time"] = start_time

    params["direction"] = direction

    params["limit"] = limit

    params["details"] = details

    params["user_uid"] = user_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/jobs",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> JobListResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as JobListResponse
        response_200 = JobListResponse.from_dict(response)

        return response_200

    return _parse_response(response)
