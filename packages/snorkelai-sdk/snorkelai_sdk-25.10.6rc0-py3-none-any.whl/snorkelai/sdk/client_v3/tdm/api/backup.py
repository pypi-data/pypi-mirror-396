# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import Backup


@overload
def get_backups_backups_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_backups_backups_get(raw: Literal[False] = False) -> List["Backup"]: ...


def get_backups_backups_get(raw: bool = False) -> List["Backup"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/backups",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Backup"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Backup']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Backup.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import cast

from ..models import OnDemandBackupRequest


def on_demand_backup_on_demand_backup_post(
    *,
    body: OnDemandBackupRequest,
) -> str:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/on-demand-backup",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> str:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as str
        # Direct parsing for str
        return cast(str, response)

    return _parse_response(response)


from ..models import RestoreBackupRequest


def restore_from_backup_restore_backup_post(
    *,
    body: RestoreBackupRequest,
) -> str:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/restore-backup",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> str:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as str
        # Direct parsing for str
        return cast(str, response)

    return _parse_response(response)
