# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import NotebookState


@overload
def get_singleuser_notebook_state_singleuser_notebook_state_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_singleuser_notebook_state_singleuser_notebook_state_get(
    raw: Literal[False] = False,
) -> NotebookState: ...


def get_singleuser_notebook_state_singleuser_notebook_state_get(
    raw: bool = False,
) -> NotebookState | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/singleuser-notebook/state",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> NotebookState:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as NotebookState
        response_200 = NotebookState.from_dict(response)

        return response_200

    return _parse_response(response)
