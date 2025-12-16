# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import Cluster


@overload
def get_cluster_cluster__cluster_uid__get(
    cluster_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_cluster_cluster__cluster_uid__get(
    cluster_uid: int, raw: Literal[False] = False
) -> Cluster: ...


def get_cluster_cluster__cluster_uid__get(
    cluster_uid: int, raw: bool = False
) -> Cluster | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/cluster/{cluster_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Cluster:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Cluster
        response_200 = Cluster.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import UpdateClusterRequest


def update_cluster_clusters__cluster_uid__put(
    cluster_uid: int,
    *,
    body: UpdateClusterRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/clusters/{cluster_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
