# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import GetSupportedPromptBuilderModelsResponse
from ..types import UNSET


@overload
def get_supported_prompt_builder_models_supported_prompt_builder_models_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_supported_prompt_builder_models_supported_prompt_builder_models_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> GetSupportedPromptBuilderModelsResponse: ...


def get_supported_prompt_builder_models_supported_prompt_builder_models_get(
    *, workspace_uid: int, raw: bool = False
) -> GetSupportedPromptBuilderModelsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/supported-prompt-builder-models",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetSupportedPromptBuilderModelsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSupportedPromptBuilderModelsResponse
        response_200 = GetSupportedPromptBuilderModelsResponse.from_dict(response)

        return response_200

    return _parse_response(response)
