# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import RayMemory


@overload
def memory_ray_memory_get(raw: Literal[True]) -> requests.Response: ...


@overload
def memory_ray_memory_get(raw: Literal[False] = False) -> RayMemory: ...


def memory_ray_memory_get(raw: bool = False) -> RayMemory | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/ray/memory",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> RayMemory:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RayMemory
        response_200 = RayMemory.from_dict(response)

        return response_200

    return _parse_response(response)
