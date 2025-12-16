# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..types import UNSET, Unset


@overload
def fetch_event_metrics_events__job_id__get(
    job_id: str, *, time_range_minutes: Union[Unset, int] = 1440, raw: Literal[True]
) -> requests.Response: ...


@overload
def fetch_event_metrics_events__job_id__get(
    job_id: str,
    *,
    time_range_minutes: Union[Unset, int] = 1440,
    raw: Literal[False] = False,
) -> Any: ...


def fetch_event_metrics_events__job_id__get(
    job_id: str, *, time_range_minutes: Union[Unset, int] = 1440, raw: bool = False
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["time_range_minutes"] = time_range_minutes

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/events/{job_id}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
