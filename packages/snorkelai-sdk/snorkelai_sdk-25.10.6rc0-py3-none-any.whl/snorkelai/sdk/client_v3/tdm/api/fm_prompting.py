# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import AugmentDatasetRequest, PromptFMResponse


def augment_dataset_augment_dataset__dataset_uid__post(
    dataset_uid: int,
    *,
    body: AugmentDatasetRequest,
) -> PromptFMResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/augment-dataset/{dataset_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptFMResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptFMResponse
        response_200 = PromptFMResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    PromptFMDatasetInBatchesRequest,
    PromptFMResponse,
)


def prompt_fm_over_dataset_in_batches_prompt_fm_in_batches__dataset_uid__post(
    dataset_uid: int,
    *,
    body: PromptFMDatasetInBatchesRequest,
) -> PromptFMResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-fm-in-batches/{dataset_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptFMResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptFMResponse
        response_200 = PromptFMResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import PromptFMDatasetRequest, PromptFMResponse


def prompt_fm_over_dataset_prompt_fm__dataset_uid__post(
    dataset_uid: int,
    *,
    body: PromptFMDatasetRequest,
) -> PromptFMResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/prompt-fm/{dataset_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptFMResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptFMResponse
        response_200 = PromptFMResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import PromptFMDatasetRequest, PromptFMResponse


def prompt_fm_over_dataset_results_prompt_fm_responses_post(
    *,
    body: PromptFMDatasetRequest,
) -> PromptFMResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/prompt-fm-responses",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptFMResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptFMResponse
        response_200 = PromptFMResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import PromptFMRequest, PromptFMResponse


def prompt_fm_prompt_fm_post(
    *,
    body: PromptFMRequest,
) -> PromptFMResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/prompt-fm",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptFMResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptFMResponse
        response_200 = PromptFMResponse.from_dict(response)

        return response_200

    return _parse_response(response)
