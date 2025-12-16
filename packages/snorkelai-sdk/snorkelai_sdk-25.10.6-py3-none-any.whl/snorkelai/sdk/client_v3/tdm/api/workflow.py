# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateWorkflowPayload, CreateWorkflowResponse


def create_workflow_workflows_post(
    *,
    body: CreateWorkflowPayload,
) -> CreateWorkflowResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workflows",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreateWorkflowResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreateWorkflowResponse
        response_201 = CreateWorkflowResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import Workflow


@overload
def get_workflow_by_id_workflows__workflow_uid__get(
    workflow_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workflow_by_id_workflows__workflow_uid__get(
    workflow_uid: int, raw: Literal[False] = False
) -> Workflow: ...


def get_workflow_by_id_workflows__workflow_uid__get(
    workflow_uid: int, raw: bool = False
) -> Workflow | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Workflow:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Workflow
        response_200 = Workflow.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import GetWorkflowResponse, WorkflowType
from ..types import UNSET, Unset


@overload
def get_workflows_workflows_get(
    *,
    workspace_uid: int,
    types: Union[Unset, List[WorkflowType]] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    input_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_workflows_workflows_get(
    *,
    workspace_uid: int,
    types: Union[Unset, List[WorkflowType]] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    input_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> List["GetWorkflowResponse"]: ...


def get_workflows_workflows_get(
    *,
    workspace_uid: int,
    types: Union[Unset, List[WorkflowType]] = UNSET,
    user_uid: Union[Unset, int] = UNSET,
    input_dataset_uid: Union[Unset, int] = UNSET,
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = UNSET,
    search: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> List["GetWorkflowResponse"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    json_types: Union[Unset, List[str]] = UNSET
    if not isinstance(types, Unset):
        json_types = []
        for types_item_data in types:
            types_item = types_item_data.value
            json_types.append(types_item)

    params["types"] = json_types

    params["user_uid"] = user_uid

    params["input_dataset_uid"] = input_dataset_uid

    params["limit"] = limit

    params["offset"] = offset

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/workflows",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["GetWorkflowResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['GetWorkflowResponse']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = GetWorkflowResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)
