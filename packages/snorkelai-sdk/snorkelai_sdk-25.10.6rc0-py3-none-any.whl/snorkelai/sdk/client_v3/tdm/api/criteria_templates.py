# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, cast

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CreateCriteriaTemplateFromCriteriaRequest
from ..types import UNSET


def create_criteria_template_from_criteria_criteria_templates_from_criteria__criteria_uid__post(
    criteria_uid: int,
    *,
    body: CreateCriteriaTemplateFromCriteriaRequest,
    workspace_uid: int,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/criteria-templates/from-criteria/{criteria_uid}",
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


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import CriteriaTemplatesListResponse
from ..types import Unset


@overload
def get_all_criteria_templates_criteria_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_all_criteria_templates_criteria_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> CriteriaTemplatesListResponse: ...


def get_all_criteria_templates_criteria_templates_get(
    *,
    workspace_uid: int,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
    search_filters: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> CriteriaTemplatesListResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["limit"] = limit

    params["offset"] = offset

    params["search_filters"] = search_filters

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/criteria-templates",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> CriteriaTemplatesListResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CriteriaTemplatesListResponse
        response_200 = CriteriaTemplatesListResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import CriteriaTemplate
from ..types import UNSET


@overload
def get_criteria_template_criteria_templates__criteria_template_uid__get(
    criteria_template_uid: int, *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_criteria_template_criteria_templates__criteria_template_uid__get(
    criteria_template_uid: int, *, workspace_uid: int, raw: Literal[False] = False
) -> CriteriaTemplate: ...


def get_criteria_template_criteria_templates__criteria_template_uid__get(
    criteria_template_uid: int, *, workspace_uid: int, raw: bool = False
) -> CriteriaTemplate | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/criteria-templates/{criteria_template_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> CriteriaTemplate:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CriteriaTemplate
        response_200 = CriteriaTemplate.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import SaveCriteriaTemplate
from ..types import UNSET


def save_criteria_as_template_criteria_templates_post(
    *,
    body: SaveCriteriaTemplate,
    workspace_uid: int,
) -> int:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/criteria-templates",
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


from ..models import (
    CriteriaTemplate,
    UpdateCriteriaTemplateRequest,
)
from ..types import UNSET


def update_criteria_template_route_criteria_templates__criteria_template_uid__put(
    criteria_template_uid: int,
    *,
    body: UpdateCriteriaTemplateRequest,
    workspace_uid: int,
) -> CriteriaTemplate:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/criteria-templates/{criteria_template_uid}",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CriteriaTemplate:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CriteriaTemplate
        response_200 = CriteriaTemplate.from_dict(response)

        return response_200

    return _parse_response(response)
