# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import CodeEvaluator, CreateOrUpdateCodePayload


def create_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code_post(
    benchmark_uid: int,
    criteria_uid: int,
    *,
    body: CreateOrUpdateCodePayload,
) -> CodeEvaluator:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/code",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CodeEvaluator:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CodeEvaluator
        response_200 = CodeEvaluator.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    CreatePromptEvaluatorForCriteriaPayload,
    CreatePromptEvaluatorResponse,
)


def create_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt_post(
    benchmark_uid: int,
    criteria_uid: int,
    *,
    body: CreatePromptEvaluatorForCriteriaPayload,
) -> CreatePromptEvaluatorResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/prompt",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> CreatePromptEvaluatorResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as CreatePromptEvaluatorResponse
        response_200 = CreatePromptEvaluatorResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet,
)


@overload
def get_all_evaluators_for_benchmark_benchmarks__benchmark_uid__evaluators_get(
    benchmark_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_all_evaluators_for_benchmark_benchmarks__benchmark_uid__evaluators_get(
    benchmark_uid: int, raw: Literal[False] = False
) -> GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet: ...


def get_all_evaluators_for_benchmark_benchmarks__benchmark_uid__evaluators_get(
    benchmark_uid: int, raw: bool = False
) -> (
    GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/evaluators",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet
        response_200 = GetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGetResponseGetAllEvaluatorsForBenchmarkBenchmarksBenchmarkUidEvaluatorsGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import (
    GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet,
)


@overload
def get_benchmark_and_criteria_uid_from_evaluator_uid_evaluators__evaluator_uid__benchmark_and_criteria_uid_get(
    evaluator_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_benchmark_and_criteria_uid_from_evaluator_uid_evaluators__evaluator_uid__benchmark_and_criteria_uid_get(
    evaluator_uid: int, raw: Literal[False] = False
) -> GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet: ...


def get_benchmark_and_criteria_uid_from_evaluator_uid_evaluators__evaluator_uid__benchmark_and_criteria_uid_get(
    evaluator_uid: int, raw: bool = False
) -> (
    GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/evaluators/{evaluator_uid}/benchmark_and_criteria_uid",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet
        response_200 = GetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGetResponseGetBenchmarkAndCriteriaUidFromEvaluatorUidEvaluatorsEvaluatorUidBenchmarkAndCriteriaUidGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..models import CodeEvaluator, PromptEvaluator


@overload
def get_criteria_evaluators_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_get(
    benchmark_uid: int, criteria_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_criteria_evaluators_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_get(
    benchmark_uid: int, criteria_uid: int, raw: Literal[False] = False
) -> List[Union["CodeEvaluator", "PromptEvaluator"]]: ...


def get_criteria_evaluators_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_get(
    benchmark_uid: int, criteria_uid: int, raw: bool = False
) -> List[Union["CodeEvaluator", "PromptEvaluator"]] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> List[Union["CodeEvaluator", "PromptEvaluator"]]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List[Union['CodeEvaluator', 'PromptEvaluator']]
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:

            def _parse_response_200_item(
                data: object,
            ) -> Union["CodeEvaluator", "PromptEvaluator"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    response_200_item_type_0 = PromptEvaluator.from_dict(data)

                    return response_200_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_item_type_1 = CodeEvaluator.from_dict(data)

                return response_200_item_type_1

            response_200_item = _parse_response_200_item(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import CodeEvaluator


@overload
def get_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators__evaluator_uid__get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators__evaluator_uid__get(
    benchmark_uid: int,
    criteria_uid: int,
    evaluator_uid: int,
    raw: Literal[False] = False,
) -> Union["CodeEvaluator", "PromptEvaluator"]: ...


def get_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators__evaluator_uid__get(
    benchmark_uid: int, criteria_uid: int, evaluator_uid: int, raw: bool = False
) -> Union["CodeEvaluator", "PromptEvaluator"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/{evaluator_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> Union["CodeEvaluator", "PromptEvaluator"]:
        """Parse response based on OpenAPI schema."""

        # Parse the success response
        # Parse as Union['CodeEvaluator', 'PromptEvaluator']
        def _parse_response_200(
            data: object,
        ) -> Union["CodeEvaluator", "PromptEvaluator"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_200_type_0 = PromptEvaluator.from_dict(data)

                return response_200_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_200_type_1 = CodeEvaluator.from_dict(data)

            return response_200_type_1

        response_200 = _parse_response_200(response)

        return response_200

    return _parse_response(response)


from ..models import (
    CreateOrUpdateCodePayload,
    UpdateCodeEvaluatorResponse,
)


def update_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__put(
    benchmark_uid: int,
    criteria_uid: int,
    evaluator_uid: int,
    *,
    body: CreateOrUpdateCodePayload,
) -> UpdateCodeEvaluatorResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/code/{evaluator_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UpdateCodeEvaluatorResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UpdateCodeEvaluatorResponse
        response_200 = UpdateCodeEvaluatorResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..types import UNSET


def update_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt__evaluator_uid__put(
    benchmark_uid: int,
    criteria_uid: int,
    evaluator_uid: int,
    *,
    prompt_uid: int,
) -> PromptEvaluator:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["prompt_uid"] = prompt_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/benchmarks/{benchmark_uid}/criteria/{criteria_uid}/evaluators/prompt/{evaluator_uid}",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PromptEvaluator:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PromptEvaluator
        response_200 = PromptEvaluator.from_dict(response)

        return response_200

    return _parse_response(response)
