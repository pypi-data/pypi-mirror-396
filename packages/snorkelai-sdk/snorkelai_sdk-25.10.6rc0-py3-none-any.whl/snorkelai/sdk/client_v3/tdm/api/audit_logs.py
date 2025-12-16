# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import GetAuditLogsResponse
from ..types import UNSET, Unset


@overload
def get_audit_logs_audit_logs_get(
    *,
    limit: Union[Unset, int] = 200,
    last_id: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_audit_logs_audit_logs_get(
    *,
    limit: Union[Unset, int] = 200,
    last_id: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> GetAuditLogsResponse: ...


def get_audit_logs_audit_logs_get(
    *,
    limit: Union[Unset, int] = 200,
    last_id: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> GetAuditLogsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["last_id"] = last_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/audit-logs",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetAuditLogsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAuditLogsResponse
        response_200 = GetAuditLogsResponse.from_dict(response)

        return response_200

    return _parse_response(response)
