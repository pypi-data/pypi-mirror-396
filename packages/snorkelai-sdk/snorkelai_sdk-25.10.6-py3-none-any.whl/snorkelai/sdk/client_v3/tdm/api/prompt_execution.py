# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


@overload
def get_criteria_uid_prompt_execution__prompt_execution_uid__criteria_get(
    prompt_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_criteria_uid_prompt_execution__prompt_execution_uid__criteria_get(
    prompt_execution_uid: int, raw: Literal[False] = False
) -> int: ...


def get_criteria_uid_prompt_execution__prompt_execution_uid__criteria_get(
    prompt_execution_uid: int, raw: bool = False
) -> int | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-execution/{prompt_execution_uid}/criteria",
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


from typing import overload

import requests
from typing_extensions import Literal


@overload
def get_workflow_uid_prompt_execution__prompt_execution_uid__workflow_get(
    prompt_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workflow_uid_prompt_execution__prompt_execution_uid__workflow_get(
    prompt_execution_uid: int, raw: Literal[False] = False
) -> int: ...


def get_workflow_uid_prompt_execution__prompt_execution_uid__workflow_get(
    prompt_execution_uid: int, raw: bool = False
) -> int | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-execution/{prompt_execution_uid}/workflow",
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
