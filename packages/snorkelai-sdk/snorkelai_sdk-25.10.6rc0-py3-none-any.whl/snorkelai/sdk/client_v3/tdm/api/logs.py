# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import ServiceType
from ..types import UNSET, Unset


@overload
def get_bundled_logs_bundled_logs_get(
    *,
    services: Union[Unset, List[ServiceType]] = UNSET,
    grep_regexes: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    number_of_lines: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_bundled_logs_bundled_logs_get(
    *,
    services: Union[Unset, List[ServiceType]] = UNSET,
    grep_regexes: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    number_of_lines: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> Any: ...


def get_bundled_logs_bundled_logs_get(
    *,
    services: Union[Unset, List[ServiceType]] = UNSET,
    grep_regexes: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    number_of_lines: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_services: Union[Unset, List[str]] = UNSET
    if not isinstance(services, Unset):
        json_services = []
        for services_item_data in services:
            services_item = services_item_data.value
            json_services.append(services_item)

    params["services"] = json_services

    json_grep_regexes: Union[Unset, List[str]] = UNSET
    if not isinstance(grep_regexes, Unset):
        json_grep_regexes = grep_regexes

    params["grep_regexes"] = json_grep_regexes

    params["workspace_uid"] = workspace_uid

    params["number_of_lines"] = number_of_lines

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/bundled-logs",
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


from typing import Any, overload

import requests
from typing_extensions import Literal


@overload
def get_job_logs_logs_job__job_id__get(
    job_id: str, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_job_logs_logs_job__job_id__get(
    job_id: str, raw: Literal[False] = False
) -> Any: ...


def get_job_logs_logs_job__job_id__get(
    job_id: str, raw: bool = False
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/logs/job/{job_id}",
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


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def get_service_logs_logs_get(
    *,
    grep_regex: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    tail_n: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_service_logs_logs_get(
    *,
    grep_regex: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    tail_n: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> Any: ...


def get_service_logs_logs_get(
    *,
    grep_regex: Union[Unset, List[str]] = UNSET,
    workspace_uid: Union[Unset, int] = UNSET,
    tail_n: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_grep_regex: Union[Unset, List[str]] = UNSET
    if not isinstance(grep_regex, Unset):
        json_grep_regex = grep_regex

    params["grep_regex"] = json_grep_regex

    params["workspace_uid"] = workspace_uid

    params["tail_n"] = tail_n

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/logs",
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def get_service_logs_v2_logs_v2_get(
    *,
    start_time: Union[Unset, str] = UNSET,
    end_time: Union[Unset, str] = UNSET,
    job_id: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_service_logs_v2_logs_v2_get(
    *,
    start_time: Union[Unset, str] = UNSET,
    end_time: Union[Unset, str] = UNSET,
    job_id: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> Any: ...


def get_service_logs_v2_logs_v2_get(
    *,
    start_time: Union[Unset, str] = UNSET,
    end_time: Union[Unset, str] = UNSET,
    job_id: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["start_time"] = start_time

    params["end_time"] = end_time

    params["job_id"] = job_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/logs-v2",
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
