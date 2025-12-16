# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import PromptTemplatesListResponse
from ..types import UNSET, Unset


@overload
def get_all_prompt_templates_prompt_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_all_prompt_templates_prompt_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> PromptTemplatesListResponse: ...


def get_all_prompt_templates_prompt_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> PromptTemplatesListResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["limit"] = limit

    params["offset"] = offset

    params["search_filters"] = search_filters

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/prompt-templates",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptTemplatesListResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptTemplatesListResponse
        response_200 = PromptTemplatesListResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import PromptTemplate
from ..types import UNSET


@overload
def get_prompt_template_prompt_templates__prompt_template_uid__get(
    prompt_template_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_prompt_template_prompt_templates__prompt_template_uid__get(
    prompt_template_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> PromptTemplate: ...


def get_prompt_template_prompt_templates__prompt_template_uid__get(
    prompt_template_uid: int, *, workspace_uid: int, raw: bool = False
) -> PromptTemplate | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-templates/{prompt_template_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptTemplate:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptTemplate
        response_200 = PromptTemplate.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import cast

from ..models import SavePromptAsTemplateRequest
from ..types import UNSET


def save_prompt_as_template_prompt_templates_post(
    *,
    body: SavePromptAsTemplateRequest,
    workspace_uid: int,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/prompt-templates",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> int:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as int
        # Direct parsing for int
        return cast(int, response)

    return _parse_response(response)


from ..models import PromptTemplate, UpdatePromptTemplateRequest
from ..types import UNSET


def update_prompt_template_route_prompt_templates__prompt_template_uid__put(
    prompt_template_uid: int,
    *,
    body: UpdatePromptTemplateRequest,
    workspace_uid: int,
) -> PromptTemplate:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-templates/{prompt_template_uid}",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptTemplate:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptTemplate
        response_200 = PromptTemplate.from_dict(response)

        return response_200

    return _parse_response(response)
