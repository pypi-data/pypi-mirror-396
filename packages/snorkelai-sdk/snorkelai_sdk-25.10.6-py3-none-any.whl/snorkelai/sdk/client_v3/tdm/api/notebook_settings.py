# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import NotebookSettings


@overload
def get_notebook_settings_notebook_settings_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_notebook_settings_notebook_settings_get(
    raw: Literal[False] = False,
) -> NotebookSettings: ...


def get_notebook_settings_notebook_settings_get(
    raw: bool = False,
) -> NotebookSettings | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/notebook-settings",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> NotebookSettings:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as NotebookSettings
        response_200 = NotebookSettings.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import NotebookSettings


def update_notebook_settings_notebook_settings_post(
    *,
    body: NotebookSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/notebook-settings",
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
