# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import AddExternalLLMConfigPayload, ExternalLLMConfig


def add_external_llm_config_external_llm_configs_post(
    *,
    body: AddExternalLLMConfigPayload,
) -> ExternalLLMConfig:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/external-llm-configs",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ExternalLLMConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ExternalLLMConfig
        response_201 = ExternalLLMConfig.from_dict(response)

        return response_201

    return _parse_response(response)


from ..types import UNSET


def delete_external_llm_config_external_llm_configs__external_llm_config_uid__delete(
    external_llm_config_uid: int,
    *,
    workspace_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/external-llm-configs/{external_llm_config_uid}",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ExternalLLMConfig


@overload
def get_external_llm_config_external_llm_configs__external_llm_config_uid__get(
    external_llm_config_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_external_llm_config_external_llm_configs__external_llm_config_uid__get(
    external_llm_config_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> ExternalLLMConfig: ...


def get_external_llm_config_external_llm_configs__external_llm_config_uid__get(
    external_llm_config_uid: int, *, workspace_uid: int, raw: bool = False
) -> ExternalLLMConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/external-llm-configs/{external_llm_config_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ExternalLLMConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ExternalLLMConfig
        response_200 = ExternalLLMConfig.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ListExternalLLMConfigsResponse


@overload
def get_external_llm_configs_external_llm_configs_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_external_llm_configs_external_llm_configs_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> ListExternalLLMConfigsResponse: ...


def get_external_llm_configs_external_llm_configs_get(
    *, workspace_uid: int, raw: bool = False
) -> ListExternalLLMConfigsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/external-llm-configs",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListExternalLLMConfigsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListExternalLLMConfigsResponse
        response_200 = ListExternalLLMConfigsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    ExternalLLMConfig,
    UpdateExternalLLMConfigPayload,
)


def update_external_llm_config_external_llm_configs__external_llm_config_uid__put(
    external_llm_config_uid: int,
    *,
    body: UpdateExternalLLMConfigPayload,
    workspace_uid: int,
) -> ExternalLLMConfig:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/external-llm-configs/{external_llm_config_uid}",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ExternalLLMConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ExternalLLMConfig
        response_200 = ExternalLLMConfig.from_dict(response)

        return response_200

    return _parse_response(response)
