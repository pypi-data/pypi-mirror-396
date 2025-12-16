# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


def cancel_prompt_execution_workflows__workflow_uid__prompts_executions__execution_uid__cancel_post(
    workflow_uid: int,
    execution_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/{execution_uid}/cancel",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import CreateNewPromptVersion, Prompt


def create_prompt_version_workflows__workflow_uid__prompts_post(
    workflow_uid: int,
    *,
    body: CreateNewPromptVersion,
) -> Prompt:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Prompt:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Prompt
        response_200 = Prompt.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def export_prompt_dev_execution_workflows__workflow_uid__prompts_executions__prompt_execution_uid__export_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    filename: Union[Unset, str] = "",
    raw: Literal[True],
) -> requests.Response: ...


@overload
def export_prompt_dev_execution_workflows__workflow_uid__prompts_executions__prompt_execution_uid__export_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    filename: Union[Unset, str] = "",
    raw: Literal[False] = False,
) -> Any: ...


def export_prompt_dev_execution_workflows__workflow_uid__prompts_executions__prompt_execution_uid__export_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    filename: Union[Unset, str] = "",
    raw: bool = False,
) -> Any | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["filename"] = filename

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/{prompt_execution_uid}/export",
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

from ..models import DataFrameResponse, Splits
from ..types import Unset


@overload
def fetch_prompt_workflow_dataframes_workflows__workflow_uid__prompts_dataframes_get(
    workflow_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    split: Union[Unset, Splits] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def fetch_prompt_workflow_dataframes_workflows__workflow_uid__prompts_dataframes_get(
    workflow_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    split: Union[Unset, Splits] = UNSET,
    raw: Literal[False] = False,
) -> DataFrameResponse: ...


def fetch_prompt_workflow_dataframes_workflows__workflow_uid__prompts_dataframes_get(
    workflow_uid: int,
    *,
    limit: Union[Unset, int] = 20,
    offset: Union[Unset, int] = 0,
    filter_config_str: Union[Unset, str] = UNSET,
    virtualized_dataset_uid: Union[Unset, int] = UNSET,
    split: Union[Unset, Splits] = UNSET,
    raw: bool = False,
) -> DataFrameResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["filter_config_str"] = filter_config_str

    params["virtualized_dataset_uid"] = virtualized_dataset_uid

    json_split: Union[Unset, str] = UNSET
    if not isinstance(split, Unset):
        json_split = split.value

    params["split"] = json_split

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts-dataframes",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DataFrameResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataFrameResponse
        response_200 = DataFrameResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import PromptEvaluator


@overload
def get_llmaj_evaluator_by_workflow_uid_workflows__workflow_uid__llmaj_evaluator_get(
    workflow_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_llmaj_evaluator_by_workflow_uid_workflows__workflow_uid__llmaj_evaluator_get(
    workflow_uid: int, raw: Literal[False] = False
) -> PromptEvaluator: ...


def get_llmaj_evaluator_by_workflow_uid_workflows__workflow_uid__llmaj_evaluator_get(
    workflow_uid: int, raw: bool = False
) -> PromptEvaluator | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/llmaj-evaluator",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptEvaluator:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptEvaluator
        response_200 = PromptEvaluator.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import PromptDevFilterStructuresResponse


@overload
def get_populated_filters_info_workflows__workflow_uid__prompts_populated_filters_info_get(
    workflow_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_populated_filters_info_workflows__workflow_uid__prompts_populated_filters_info_get(
    workflow_uid: int, raw: Literal[False] = False
) -> PromptDevFilterStructuresResponse: ...


def get_populated_filters_info_workflows__workflow_uid__prompts_populated_filters_info_get(
    workflow_uid: int, raw: bool = False
) -> PromptDevFilterStructuresResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts-populated-filters-info",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptDevFilterStructuresResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptDevFilterStructuresResponse
        response_200 = PromptDevFilterStructuresResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import Prompt


@overload
def get_prompt_workflows__workflow_uid__prompts__prompt_uid__get(
    workflow_uid: int, prompt_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_prompt_workflows__workflow_uid__prompts__prompt_uid__get(
    workflow_uid: int, prompt_uid: int, raw: Literal[False] = False
) -> Prompt: ...


def get_prompt_workflows__workflow_uid__prompts__prompt_uid__get(
    workflow_uid: int, prompt_uid: int, raw: bool = False
) -> Prompt | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/{prompt_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Prompt:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Prompt
        response_200 = Prompt.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import Prompt


@overload
def get_prompts_workflows__workflow_uid__prompts_get(
    workflow_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_prompts_workflows__workflow_uid__prompts_get(
    workflow_uid: int, raw: Literal[False] = False
) -> List["Prompt"]: ...


def get_prompts_workflows__workflow_uid__prompts_get(
    workflow_uid: int, raw: bool = False
) -> List["Prompt"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["Prompt"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['Prompt']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = Prompt.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import EvaluationMetric


@overload
def prompt_execution_metrics_workflows__workflow_uid__prompts_executions__prompt_execution_uid__metrics_get(
    workflow_uid: int, prompt_execution_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def prompt_execution_metrics_workflows__workflow_uid__prompts_executions__prompt_execution_uid__metrics_get(
    workflow_uid: int, prompt_execution_uid: int, raw: Literal[False] = False
) -> List["EvaluationMetric"]: ...


def prompt_execution_metrics_workflows__workflow_uid__prompts_executions__prompt_execution_uid__metrics_get(
    workflow_uid: int, prompt_execution_uid: int, raw: bool = False
) -> List["EvaluationMetric"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/{prompt_execution_uid}/metrics",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["EvaluationMetric"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['EvaluationMetric']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = EvaluationMetric.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import PromptDevExecutionVersionResponse
from ..types import UNSET, Unset


@overload
def prompt_execution_response_workflows__workflow_uid__prompts_executions__prompt_execution_uid__responses_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def prompt_execution_response_workflows__workflow_uid__prompts_executions__prompt_execution_uid__responses_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: Literal[False] = False,
) -> PromptDevExecutionVersionResponse: ...


def prompt_execution_response_workflows__workflow_uid__prompts_executions__prompt_execution_uid__responses_get(
    workflow_uid: int,
    prompt_execution_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    raw: bool = False,
) -> PromptDevExecutionVersionResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/{prompt_execution_uid}/responses",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptDevExecutionVersionResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptDevExecutionVersionResponse
        response_200 = PromptDevExecutionVersionResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import PromptDevGetScoreResponse
from ..types import UNSET, Unset


@overload
def prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get(
    workflow_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get(
    workflow_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[False] = False,
) -> PromptDevGetScoreResponse: ...


def prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get(
    workflow_uid: int,
    *,
    x_uids: Union[Unset, List[str]] = UNSET,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: bool = False,
) -> PromptDevGetScoreResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    json_x_uids: Union[Unset, List[str]] = UNSET
    if not isinstance(x_uids, Unset):
        json_x_uids = x_uids

    params["x_uids"] = json_x_uids

    json_prompt_execution_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(prompt_execution_uids, Unset):
        json_prompt_execution_uids = prompt_execution_uids

    params["prompt_execution_uids"] = json_prompt_execution_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/scores",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptDevGetScoreResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptDevGetScoreResponse
        response_200 = PromptDevGetScoreResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import PromptDevExecutionXuidResponse
from ..types import UNSET, Unset


@overload
def prompt_responses_for_x_uid_workflows__workflow_uid__prompts_executions_responses_get(
    workflow_uid: int,
    *,
    x_uid: str,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def prompt_responses_for_x_uid_workflows__workflow_uid__prompts_executions_responses_get(
    workflow_uid: int,
    *,
    x_uid: str,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: Literal[False] = False,
) -> PromptDevExecutionXuidResponse: ...


def prompt_responses_for_x_uid_workflows__workflow_uid__prompts_executions_responses_get(
    workflow_uid: int,
    *,
    x_uid: str,
    prompt_execution_uids: Union[Unset, List[int]] = UNSET,
    raw: bool = False,
) -> PromptDevExecutionXuidResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["x_uid"] = x_uid

    json_prompt_execution_uids: Union[Unset, List[int]] = UNSET
    if not isinstance(prompt_execution_uids, Unset):
        json_prompt_execution_uids = prompt_execution_uids

    params["prompt_execution_uids"] = json_prompt_execution_uids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions/responses",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> PromptDevExecutionXuidResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptDevExecutionXuidResponse
        response_200 = PromptDevExecutionXuidResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    PromptDevStartExecutionRequest,
    PromptDevStartExecutionResponse,
)


def start_prompt_dev_execution_workflows__workflow_uid__prompts_executions_post(
    workflow_uid: int,
    *,
    body: PromptDevStartExecutionRequest,
) -> PromptDevStartExecutionResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/executions",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptDevStartExecutionResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptDevStartExecutionResponse
        response_200 = PromptDevStartExecutionResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import Prompt, PromptDevPatchPromptRequest


def update_prompt_workflows__workflow_uid__prompts__prompt_uid__patch(
    workflow_uid: int,
    prompt_uid: int,
    *,
    body: PromptDevPatchPromptRequest,
) -> Prompt:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workflows/{workflow_uid}/prompts/{prompt_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Prompt:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as Prompt
        response_200 = Prompt.from_dict(response)

        return response_200

    return _parse_response(response)
