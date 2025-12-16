# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    DeleteIntegrationFmIntegrationsProviderDeleteKwargs,
    ExternalLLMProvider,
)
from ..types import UNSET, Unset


def delete_integration_fm_integrations__provider__delete(
    provider: ExternalLLMProvider,
    *,
    body: DeleteIntegrationFmIntegrationsProviderDeleteKwargs,
    secret_store: Union[Unset, str] = "local_store",
    workspace_uid: Union[Unset, int] = 1,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["secret_store"] = secret_store

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/fm-integrations/{provider}",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ExternalLLMProvider, FMProviderStatusResponse


@overload
def get_fm_provider_status_fm_integrations__provider__status_get(
    provider: ExternalLLMProvider, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_fm_provider_status_fm_integrations__provider__status_get(
    provider: ExternalLLMProvider, *, workspace_uid: int, raw: Literal[False] = False
) -> FMProviderStatusResponse: ...


def get_fm_provider_status_fm_integrations__provider__status_get(
    provider: ExternalLLMProvider, *, workspace_uid: int, raw: bool = False
) -> FMProviderStatusResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/fm-integrations/{provider}/status",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> FMProviderStatusResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as FMProviderStatusResponse
        response_200 = FMProviderStatusResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    ListIntegrationsParams,
    ListIntegrationsResponse,
)


def list_integrations_fm_integrations_put(
    *,
    body: ListIntegrationsParams,
) -> ListIntegrationsResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/fm-integrations",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> ListIntegrationsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListIntegrationsResponse
        response_200 = ListIntegrationsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import ExternalLLMProvider, SetIntegrationParams


def set_integration_fm_integrations__provider__post(
    provider: ExternalLLMProvider,
    *,
    body: SetIntegrationParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/fm-integrations/{provider}",
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
