# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    ApplyDatasetTemplatePayload,
    ApplyDatasetTemplateResponse,
)


def apply_dataset_template_datasets__dataset_uid__apply_template_post(
    dataset_uid: int,
    *,
    body: ApplyDatasetTemplatePayload,
) -> ApplyDatasetTemplateResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/apply-template",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ApplyDatasetTemplateResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ApplyDatasetTemplateResponse
        response_200 = ApplyDatasetTemplateResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasetTemplate
from ..types import UNSET, Unset


@overload
def get_dataset_templates_dataset_templates_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_dataset_templates_dataset_templates_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: Literal[False] = False
) -> List["DatasetTemplate"]: ...


def get_dataset_templates_dataset_templates_get(
    *, workspace_uid: Union[Unset, int] = 1, raw: bool = False
) -> List["DatasetTemplate"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/dataset-templates",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetTemplate"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetTemplate']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetTemplate.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)
