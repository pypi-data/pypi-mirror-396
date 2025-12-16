# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import FetchNodeResponse


@overload
def fetch_node_nodes__node_uid__get(
    node_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_node_nodes__node_uid__get(
    node_uid: int, raw: Literal[False] = False
) -> FetchNodeResponse: ...


def fetch_node_nodes__node_uid__get(
    node_uid: int, raw: bool = False
) -> FetchNodeResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> FetchNodeResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as FetchNodeResponse
        response_200 = FetchNodeResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import cast, overload

import requests
from typing_extensions import Literal


@overload
def get_dataset_from_node_nodes__node_uid__dataset_uid_get(
    node_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_dataset_from_node_nodes__node_uid__dataset_uid_get(
    node_uid: int, raw: Literal[False] = False
) -> int: ...


def get_dataset_from_node_nodes__node_uid__dataset_uid_get(
    node_uid: int, raw: bool = False
) -> int | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/nodes/{node_uid}/dataset_uid",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> int:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as int
        # Direct parsing for int
        return cast(int, response)

    return _parse_response(response)
