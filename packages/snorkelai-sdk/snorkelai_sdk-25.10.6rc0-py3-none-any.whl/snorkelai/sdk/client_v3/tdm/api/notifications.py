# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


def delete_notification_notifications__notification_uid__delete(
    notification_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/notifications/{notification_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any


def delete_notifications_notifications_delete() -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/notifications",
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

from ..models import Notification


@overload
def get_notification_notifications__notification_uid__get(
    notification_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_notification_notifications__notification_uid__get(
    notification_uid: int, raw: Literal[False] = False
) -> Notification: ...


def get_notification_notifications__notification_uid__get(
    notification_uid: int, raw: bool = False
) -> Notification | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/notifications/{notification_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Notification:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Notification
        response_200 = Notification.from_dict(response)

        return response_200

    return _parse_response(response)


import datetime
from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import ListNotificationsResponse
from ..types import UNSET, Unset


@overload
def list_notifications_notifications_get(
    *,
    max_: Union[Unset, int] = UNSET,
    start_timestamp: Union[Unset, datetime.datetime] = UNSET,
    end_timestamp: Union[Unset, datetime.datetime] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_notifications_notifications_get(
    *,
    max_: Union[Unset, int] = UNSET,
    start_timestamp: Union[Unset, datetime.datetime] = UNSET,
    end_timestamp: Union[Unset, datetime.datetime] = UNSET,
    raw: Literal[False] = False,
) -> ListNotificationsResponse: ...


def list_notifications_notifications_get(
    *,
    max_: Union[Unset, int] = UNSET,
    start_timestamp: Union[Unset, datetime.datetime] = UNSET,
    end_timestamp: Union[Unset, datetime.datetime] = UNSET,
    raw: bool = False,
) -> ListNotificationsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["max"] = max_

    json_start_timestamp: Union[Unset, str] = UNSET
    if not isinstance(start_timestamp, Unset):
        json_start_timestamp = start_timestamp.isoformat()
    params["start_timestamp"] = json_start_timestamp

    json_end_timestamp: Union[Unset, str] = UNSET
    if not isinstance(end_timestamp, Unset):
        json_end_timestamp = end_timestamp.isoformat()
    params["end_timestamp"] = json_end_timestamp

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/notifications",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> ListNotificationsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListNotificationsResponse
        response_200 = ListNotificationsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import UpdateNotificationPayload


def update_notification_status_notifications__notification_uid__patch(
    notification_uid: int,
    *,
    body: UpdateNotificationPayload,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/notifications/{notification_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
