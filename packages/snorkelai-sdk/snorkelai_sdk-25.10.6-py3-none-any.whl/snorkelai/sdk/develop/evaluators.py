import inspect
from abc import ABC, abstractmethod
from collections import defaultdict
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast, final

import pandas as pd
from typing_extensions import override

from snorkelai.sdk.client_v3.tdm.api.code import (
    execute_code_version_code_version__code_version_uid__execute_post,
    get_code_execution_code_execution__code_execution_uid__get,
    get_code_execution_results_code_execution__code_execution_uid__results_get,
    list_code_executions_by_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__executions_get,
    list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get,
)
from snorkelai.sdk.client_v3.tdm.api.criteria import (
    get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get,
)
from snorkelai.sdk.client_v3.tdm.api.evaluator import (
    create_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code_post,
    create_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt_post,
    get_benchmark_and_criteria_uid_from_evaluator_uid_evaluators__evaluator_uid__benchmark_and_criteria_uid_get,
    get_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators__evaluator_uid__get,
    update_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__put,
    update_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt__evaluator_uid__put,
)
from snorkelai.sdk.client_v3.tdm.api.jobs import (
    get_job_for_uid_jobs__job_uid__get,
)
from snorkelai.sdk.client_v3.tdm.api.prompt_development import (
    create_prompt_version_workflows__workflow_uid__prompts_post,
    get_prompts_workflows__workflow_uid__prompts_get,
    prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get,
    start_prompt_dev_execution_workflows__workflow_uid__prompts_executions_post,
)
from snorkelai.sdk.client_v3.tdm.models import (
    EvaluationScoreWithPromptExecutionUid,
    PromptDevExecutionJobStatus,
    PromptDevGetScoreResponse,
    PromptDevStartExecutionRequest,
)
from snorkelai.sdk.client_v3.tdm.models.code_evaluator import (
    CodeEvaluator as CodeEvaluatorApiModel,
)
from snorkelai.sdk.client_v3.tdm.models.create_new_prompt_version import (
    CreateNewPromptVersion,
)
from snorkelai.sdk.client_v3.tdm.models.create_new_prompt_version_fm_hyperparameters import (
    CreateNewPromptVersionFmHyperparameters,
)
from snorkelai.sdk.client_v3.tdm.models.create_or_update_code_payload import (
    CreateOrUpdateCodePayload,
)
from snorkelai.sdk.client_v3.tdm.models.create_prompt_evaluator_for_criteria_payload import (
    CreatePromptEvaluatorForCriteriaPayload,
)
from snorkelai.sdk.client_v3.tdm.models.execute_code_version_request import (
    ExecuteCodeVersionRequest,
)
from snorkelai.sdk.client_v3.tdm.models.execution_vds_metadata import (
    ExecutionVDSMetadata,
)
from snorkelai.sdk.client_v3.tdm.models.prompt import Prompt
from snorkelai.sdk.client_v3.tdm.models.prompt_evaluator import (
    PromptEvaluator as PromptEvaluatorApiModel,
)
from snorkelai.sdk.client_v3.tdm.models.splits import Splits
from snorkelai.sdk.client_v3.tdm.types import UNSET, Unset
from snorkelai.sdk.client_v3.utils import _wrap_in_unset, poll_job_status
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.types.jobs import JobState

EvaluationScoreType = Union[str, int, float, bool]


class Evaluator(ABC, Base):
    """
    Base class for all evaluators.

    An evaluator assesses a datapoint containing an AI application's response
    against a specific criteria. Evaluators can be of two types:

    - **CodeEvaluator**: Code-based (using custom Python functions)
    - **PromptEvaluator**: Prompt-based (using LLM prompts)

    The goal of an evaluator is to categorize the datapoint into one of the
    criteria's labels, ultimately assigning the integer associated with the
    label as that datapoint's score. An evaluator can also assign a rationale
    for its score, which is used to explain the score.

    Read more in the `Evaluation overview <https://docs.snorkel.ai/docs/user-guide/evaluation/evaluation-overview>`_.

    Using the ``Evaluator`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import Evaluator
    """

    _benchmark_uid: int
    _criteria_uid: int
    _evaluator_uid: int

    def __init__(
        self,
        benchmark_uid: int,
        criteria_uid: int,
        evaluator_uid: int,
    ):
        """
        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark that contains the criteria.
            The ``benchmark_uid`` is visible in the URL of the benchmark page in
            the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.
        criteria_uid
            The unique identifier of the criteria that this evaluator assesses.
        evaluator_uid
            The unique identifier for this evaluator.
        """
        self._benchmark_uid = benchmark_uid
        self._criteria_uid = criteria_uid
        self._evaluator_uid = evaluator_uid

    @property
    def uid(self) -> int:
        """Return the UID of the evaluator"""
        return self._evaluator_uid

    @property
    def evaluator_uid(self) -> int:
        """Return the UID of the evaluator"""
        # This is only for backcompat
        return self._evaluator_uid

    @property
    def benchmark_uid(self) -> int:
        """Return the UID of the parent benchmark"""
        return self._benchmark_uid

    @property
    def criteria_uid(self) -> int:
        """Return the UID of the parent criteria"""
        return self._criteria_uid

    @staticmethod
    def _get_evaluator_by_uid(
        evaluator_uid: int,
    ) -> Tuple[int, int, CodeEvaluatorApiModel | PromptEvaluatorApiModel]:
        benchmark_criteria_uid_response = get_benchmark_and_criteria_uid_from_evaluator_uid_evaluators__evaluator_uid__benchmark_and_criteria_uid_get(
            evaluator_uid=evaluator_uid,
        )
        benchmark_uid = benchmark_criteria_uid_response["benchmark_uid"]
        criteria_uid = benchmark_criteria_uid_response["criteria_uid"]

        evaluator_response = get_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators__evaluator_uid__get(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            evaluator_uid=evaluator_uid,
        )
        return benchmark_uid, criteria_uid, evaluator_response

    @staticmethod
    def _from_api_model(
        benchmark_uid: int,
        evaluator_response: CodeEvaluatorApiModel | PromptEvaluatorApiModel,
    ) -> "Evaluator":
        """
        Internal method to convert an evaluator API model to an Evaluator object.
        Since the API model doesn't contain the benchmark_uid, we need to manually supply it to this function.
        """
        if isinstance(evaluator_response, CodeEvaluatorApiModel):
            return CodeEvaluator(
                benchmark_uid=benchmark_uid,
                criteria_uid=evaluator_response.criteria_uid,
                evaluator_uid=evaluator_response.evaluator_uid,
            )
        elif isinstance(evaluator_response, PromptEvaluatorApiModel):
            return PromptEvaluator(
                benchmark_uid=benchmark_uid,
                criteria_uid=evaluator_response.criteria_uid,
                evaluator_uid=evaluator_response.evaluator_uid,
                prompt_workflow_uid=evaluator_response.prompt_workflow_uid,
            )
        else:
            raise ValueError(f"Unknown evaluator type: {evaluator_response.type}")

    @classmethod
    def get(cls, evaluator_uid: int) -> "Evaluator":
        """Retrieves the evaluator for a given uid.

        Parameters
        ----------
        evaluator_uid
            The unique identifier for the evaluator.

        Returns
        -------
        Evaluator
            The requested evaluator object.

        Example
        -------
        .. testcode::

            evaluator = Evaluator.get(evaluator_uid=300)
        """
        benchmark_uid, _, evaluator_response = Evaluator._get_evaluator_by_uid(
            evaluator_uid
        )

        return Evaluator._from_api_model(benchmark_uid, evaluator_response)

    @classmethod
    @abstractmethod
    def create(cls, *args: Any, **kwargs: Any) -> "Evaluator":
        """Creates a new evaluator for a criteria.

        Parameters
        ----------
        args
            Parameters specific to the evaluator type.
        kwargs
            Parameters specific to the evaluator type.
        """

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> None:
        """Updates the evaluator with a new version.

        Parameters
        ----------
        args
            Parameters specific to the evaluator type.
        kwargs
            Parameters specific to the evaluator type.
        """

    @abstractmethod
    def get_versions(self) -> List[str]:
        """Retrieves all version names for this evaluator."""

    @abstractmethod
    def execute(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> int:
        """Runs the evaluator against all datapoints in the specified dataset
        split.

        Parameters
        ----------
        args
            Parameters specific to the evaluator type.
        kwargs
            Parameters specific to the evaluator type.
        """

    @abstractmethod
    def get_execution_result(
        self, execution_uid: int
    ) -> Dict[str, Dict[str, EvaluationScoreType]]:
        """Retrieves the evaluation results and scores for a specific execution.

        Parameters
        ----------
        execution_uid
            The unique identifier of the execution you want to get results for.
        """

    @abstractmethod
    def poll_execution_result(
        self, execution_uid: int, sync: bool = False
    ) -> Tuple[str, Dict[str, Dict[str, EvaluationScoreType]]]:
        """Polls the evaluation job status and retrieves partial results.

        Parameters
        ----------
        execution_uid
            The unique identifier of the execution you want to poll for.
        sync
            Whether to wait for the job to complete.
        """

    @abstractmethod
    def get_executions(self) -> List[Dict[str, Any]]:
        """Retrieves all executions for this evaluator."""

    @classmethod
    def delete(cls, evaluator_uid: int) -> None:
        """Deletion of an evaluator is not implemented.

        Parameters
        ----------
        evaluator_uid
            The unique identifier of the evaluator.
        """
        raise NotImplementedError("Not implemented")


@final
class PromptEvaluator(Evaluator):
    """An evaluator that uses LLM prompts to assess model outputs.

    This evaluator type is known as an LLM-as-a-judge (LLMAJ). A prompt
    evaluator uses LLM prompts to evaluate datapoints containing AI application
    responses, categorizing them into one of a criteria's labels by assigning
    the corresponding integer score and optional rationale.

    Prompt evaluator execution via the SDK is not yet supported. Please use the GUI to run prompt evaluators.

    Read more about `LLM-as-a-judge <https://docs.snorkel.ai/docs/user-guide/evaluation/create-llmaj-prompt>`_ prompts.

    Using the ``PromptEvaluator`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import PromptEvaluator
    """

    _prompt_workflow_uid: int

    def __init__(
        self,
        benchmark_uid: int,
        criteria_uid: int,
        evaluator_uid: int,
        prompt_workflow_uid: int,
    ):
        """
        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark that contains the criteria.
        criteria_uid
            The unique identifier of the criteria that this evaluator assesses.
        evaluator_uid
            The unique identifier for this evaluator.
        prompt_workflow_uid
            The unique identifier of the parent prompt workflow.
        """
        super().__init__(benchmark_uid, criteria_uid, evaluator_uid)
        self._prompt_workflow_uid = prompt_workflow_uid

    @property
    def prompt_workflow_uid(self) -> int:
        """Return the UID of the parent prompt workflow"""
        return self._prompt_workflow_uid

    @override
    @classmethod
    def get(cls, evaluator_uid: int) -> "PromptEvaluator":
        """Retrieves a prompt evaluator for a given uid.

        Parameters
        ----------
        evaluator_uid
            The unique identifier for the evaluator.

        Returns
        -------
        PromptEvaluator
            A PromptEvaluator instance.

        Raises
        ------
        ValueError
            If the evaluator with the given uid is not a PromptEvaluator.
        """
        evaluator = super().get(evaluator_uid)
        if not isinstance(evaluator, PromptEvaluator):
            raise ValueError(f"Evaluator {evaluator_uid} is not a PromptEvaluator")
        return evaluator

    @override
    @classmethod
    def create(
        cls,
        criteria_uid: int,
        user_prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        fm_hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> "PromptEvaluator":
        """Creates a new prompt evaluator for a criteria.

        Parameters
        ----------
        criteria_uid
            The unique identifier of the criteria that this evaluator assesses.
        user_prompt
            The user prompt to use for the evaluator. At least one of user_prompt or system_prompt must be provided.
        system_prompt
            The system prompt to use for the evaluator. At least one of user_prompt or system_prompt must be provided.
        model_name
            The model to use for the evaluator.
        fm_hyperparameters
            The hyperparameters to use for the evaluator. These are provided directly to the model provider.

            For example, OpenAI supports the `response_format` hyperparameter. It can be provided in the following way:

            .. testcode::

                PromptEvaluator.create(
                    criteria_uid=100,
                    user_prompt="User prompt",
                    system_prompt="System prompt",
                    model_name="gpt-4o-mini",
                    fm_hyperparameters={
                        "response_format": {
                            "type": "json_object",
                        }
                    }
                )

            Or a more sophisticated example:

            .. testcode::

                PromptEvaluator.create(
                    criteria_uid=100,
                    user_prompt="User prompt",
                    system_prompt="System prompt",
                    model_name="gpt-4o-mini",
                    fm_hyperparameters={
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "math_reasoning",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "steps": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "explanation": {"type": "string"},
                                                    "output": {"type": "string"}
                                                },
                                                "required": ["explanation", "output"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "final_answer": {"type": "string"}
                                    },
                                    "required": ["steps", "final_answer"],
                                    "additionalProperties": False
                                },
                                "strict": True
                            }
                        }
                    }
                )

        Returns
        -------
        PromptEvaluator
            A PromptEvaluator object representing the new evaluator.

        Raises
        ------
        ValueError
            If one of user_prompt, system_prompt is not provided.
            If model_name is not provided.
        """
        # Get benchmark UID from criteria UID
        benchmark_uid = get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
            criteria_uid=criteria_uid
        )

        # Validate that at least one prompt is provided
        if not user_prompt and not system_prompt:
            raise ValueError(
                "At least one of user_prompt or system_prompt must be provided"
            )

        if not model_name:
            raise ValueError("model_name is required")

        # Create prompt configuration
        hyperparams: CreateNewPromptVersionFmHyperparameters | Unset = (
            CreateNewPromptVersionFmHyperparameters.from_dict(fm_hyperparameters)
            if fm_hyperparameters is not None
            else UNSET
        )

        prompt_configuration = CreateNewPromptVersion(
            model_name=model_name,
            user_prompt=_wrap_in_unset(user_prompt),
            system_prompt=_wrap_in_unset(system_prompt),
            fm_hyperparameters=hyperparams,
        )

        # Create payload
        payload = CreatePromptEvaluatorForCriteriaPayload(
            prompt_configuration=prompt_configuration
        )

        # Create the prompt evaluator
        response = create_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt_post(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            body=payload,
        )

        return cls(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            evaluator_uid=response.prompt_evaluator.evaluator_uid,
            prompt_workflow_uid=response.prompt_evaluator.prompt_workflow_uid,
        )

    @override
    def update(
        self,
        version_name: Optional[str] = None,
        user_prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        fm_hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Creates a new prompt version for a criteria and updates the evaluator to point to the new prompt version.

        Parameters
        ----------
        version_name
            The name for the new prompt version. If not provided, a default name will be generated.
        user_prompt
            The user prompt to use for the evaluator. At least one of user_prompt or system_prompt must be provided.
        system_prompt
            The system prompt to use for the evaluator. At least one of user_prompt or system_prompt must be provided.
        model_name
            The model to use for the evaluator.
        fm_hyperparameters
            The hyperparameters to use for the evaluator. These are provided directly to the model provider.

            For example, OpenAI supports the `response_format` hyperparameter. It can be provided in the following way:

            .. testcode::

                evaluator = PromptEvaluator.get(evaluator_uid=300)
                evaluator.update(
                    version_name="New Version",
                    user_prompt="User prompt",
                    system_prompt="System prompt",
                    model_name="gpt-4o-mini",
                    fm_hyperparameters={
                        "response_format": {
                            "type": "json_object",
                        }
                    }
                )

            Or a more sophisticated example:

            .. testcode::

                evaluator = PromptEvaluator.get(evaluator_uid=300)
                evaluator.update(
                    version_name="New Version",
                    user_prompt="User prompt",
                    system_prompt="System prompt",
                    model_name="gpt-4o-mini",
                    fm_hyperparameters={
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "math_reasoning",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "steps": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "explanation": {"type": "string"},
                                                    "output": {"type": "string"}
                                                },
                                                "required": ["explanation", "output"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "final_answer": {"type": "string"}
                                    },
                                    "required": ["steps", "final_answer"],
                                    "additionalProperties": False
                                },
                                "strict": True
                            }
                        }
                    }
                )

        Raises
        ------
        ValueError
            If one of user_prompt, system_prompt is not provided.
            If model_name is not provided.
        """
        # Validate that at least one prompt is provided
        if not user_prompt and not system_prompt:
            raise ValueError(
                "At least one of user_prompt or system_prompt must be provided"
            )

        if not model_name:
            raise ValueError("model_name is required")

        # Create new prompt version
        hyperparams: CreateNewPromptVersionFmHyperparameters | Unset = (
            CreateNewPromptVersionFmHyperparameters.from_dict(fm_hyperparameters)
            if fm_hyperparameters is not None
            else UNSET
        )

        prompt_version_payload = CreateNewPromptVersion(
            model_name=str(model_name),
            prompt_version_name=_wrap_in_unset(version_name),
            user_prompt=_wrap_in_unset(user_prompt),
            system_prompt=_wrap_in_unset(system_prompt),
            fm_hyperparameters=hyperparams,
        )

        # Create the new prompt version
        prompt_response = create_prompt_version_workflows__workflow_uid__prompts_post(
            workflow_uid=self.prompt_workflow_uid,
            body=prompt_version_payload,
        )

        new_prompt_uid = prompt_response.prompt_uid

        # Update the evaluator to point to the new prompt version
        update_prompt_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_prompt__evaluator_uid__put(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
            prompt_uid=new_prompt_uid,
        )

    def _get_prompt_versions(self) -> List[Prompt]:
        prompts_response = get_prompts_workflows__workflow_uid__prompts_get(
            workflow_uid=self.prompt_workflow_uid
        )
        return prompts_response

    @override
    def get_versions(self) -> List[str]:
        """
        Gets all version names for a prompt evaluator.

        Returns
        -------
        List[str]
            A list of version names for the prompt evaluator.
        """
        # Get all prompts for the workflow
        prompts = self._get_prompt_versions()

        # Extract version names from the response
        version_names = [prompt.prompt_version_name for prompt in prompts]

        return version_names

    @override
    def execute(
        self,
        split: str,
        num_rows: Optional[int] = None,
        version_name: Optional[str] = None,
        sync: bool = False,
    ) -> int:
        """Executes the prompt evaluator against a dataset split.

        This method runs the prompt against the specified dataset split.
        If no version name is specified, it uses the latest version.

        Parameters
        ----------
        split
            The dataset split to evaluate on.
        num_rows
            The number of rows to evaluate on.
        version_name
            The version name to use for the execution. If not provided, it uses the latest version.
        sync
            Whether to wait for the execution to complete.

        Returns
        -------
        int
            The execution uid.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Execute the latest prompt version and poll for results:

        .. testcode::

            import time

            evaluator = PromptEvaluator.get(evaluator_uid=300)
            prompt_execution_uid = evaluator.execute(split="test", num_rows=100)
            while True:
                status, results = evaluator.poll_execution_result(prompt_execution_uid, sync=False)
                print(f"Job status: {status}")
                if status == "completed" or status == "failed":
                    break
                if results:
                    print(f"Partial results: {results}")
                time.sleep(10)

            print(f"Final results: {results}")

        Example 2
        ^^^^^^^^^

        Execute a specific prompt version and wait for results:

        .. testcode::

            evaluator = PromptEvaluator.get(evaluator_uid=300)
            prompt_execution_uid = evaluator.execute(split="train", num_rows=20, version_name="v1.0")
            status, results = evaluator.poll_execution_result(prompt_execution_uid, sync=True)
            print(f"Status: {status}")
            print(f"Results: {results}")
        """
        # For prompt evaluators, the version maps to the prompt uid
        # so we need to get the prompt uid from the version name
        prompts = self._get_prompt_versions()
        if version_name is not None:
            prompt_uid = next(
                (
                    prompt.prompt_uid
                    for prompt in prompts
                    if prompt.prompt_version_name == version_name
                ),
                None,
            )
            if prompt_uid is None:
                raise ValueError(f"Prompt version {version_name} not found")
        else:
            prompt_uid = sorted(prompts, key=lambda x: x.created_at)[-1].prompt_uid

        # Start the execution
        response = (
            start_prompt_dev_execution_workflows__workflow_uid__prompts_executions_post(
                workflow_uid=self.prompt_workflow_uid,
                body=PromptDevStartExecutionRequest(
                    prompt_uid=prompt_uid,
                    filter_options=ExecutionVDSMetadata(
                        splits=[Splits(split)],
                        first_n_indexes=_wrap_in_unset(num_rows),
                    ),
                ),
            )
        )

        # Get the inner Engine job id and confirm the job is valid
        job_id = response.job_id
        if isinstance(job_id, Unset):
            raise ValueError(
                f"Cannot find the job_id for execution {response.prompt_execution_uid}"
            )

        if sync:
            # Block until the Engine job completes or fails
            # We call poll_job_status() on the Engine job_id instead of
            # poll_execution_result() on the prompt_execution_uid because
            # poll_job_status() is very lightweight as it only checks the status cache
            poll_job_status(job_id)

        return response.prompt_execution_uid

    def _parse_execution_scores(
        self, execution_uid: int, scores: List[EvaluationScoreWithPromptExecutionUid]
    ) -> Dict[str, Dict[str, EvaluationScoreType]]:
        results: Dict[str, Dict[str, EvaluationScoreType]] = defaultdict(defaultdict)
        for score in scores:
            if (
                score.prompt_execution_uid == execution_uid
                and score.value is not None
                and score.value != "None"
                and score.value is not Unset
            ):
                results[score.x_uid][score.type.value] = cast(
                    EvaluationScoreType, score.value
                )
        return results

    @override
    def get_execution_result(
        self, execution_uid: int
    ) -> Dict[str, Dict[str, EvaluationScoreType]]:
        """Retrieves the evaluation results for a specific evaluation execution.

        This method reads the evaluation results for the given evaluation execution UID.
        If the execution is in progress, it will return partial results.

        Parameters
        ----------
        execution_uid
            The evaluation execution UID to get results for.

        Returns
        -------
        Dict[str, Dict[str, EvaluationScoreType]]
            A dictionary mapping x_uids to their evaluation results.
            The evaluation results for each x_uid are a dictionary with the following keys:
            - "score": The score for the datapoint
            - "rationale": The rationale for the score
        """
        response: PromptDevGetScoreResponse = (
            prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get(
                workflow_uid=self.prompt_workflow_uid,
                prompt_execution_uids=[execution_uid],
            )
        )
        return self._parse_execution_scores(execution_uid, response.scores)

    @override
    def poll_execution_result(
        self, execution_uid: int, sync: bool = False
    ) -> Tuple[str, Dict[str, Dict[str, EvaluationScoreType]]]:
        """Polls the job status and retrieves partial results.

        This method checks the current status of the evaluation job and returns
        both the job status and any available results. The current status
        can be ``running``, ``completed``, ``failed``, ``cancelled``, or ``unknown``.

        Parameters
        ----------
        execution_uid
            The prompt execution UID to poll for.
        sync
            Whether to wait for the job to complete. If ``False``, returns immediately
            with current status and partial results.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Poll for job status and partial results:

        .. testcode::

            evaluator = PromptEvaluator.get(evaluator_uid=300)
            prompt_execution_uid = evaluator.execute(split="test", num_rows=100)
            while True:
                status, results = evaluator.poll_execution_result(prompt_execution_uid, sync=False)
                print(f"Job status: {status}")
                if results:
                    print(f"Partial results: {results}")
                if status == "completed" or status == "failed":
                    break
            print(f"Final results: {results}")
        """
        response: PromptDevGetScoreResponse = (
            prompt_execution_scores_workflows__workflow_uid__prompts_executions_scores_get(
                workflow_uid=self.prompt_workflow_uid,
                prompt_execution_uids=[execution_uid],
            )
        )
        execution_job: PromptDevExecutionJobStatus | None = next(
            (
                execution_job
                for execution_job in response.execution_jobs
                if execution_job.prompt_execution_uid == execution_uid
            ),
            None,
        )
        if execution_job is None:
            raise ValueError(f"Execution {execution_uid} not found")

        # Return immediately if sync is False or if the job is completed
        if not sync or execution_job.job_status == JobState.COMPLETED:
            return execution_job.job_status.value, self._parse_execution_scores(
                execution_uid, response.scores
            )
        job_id = execution_job.job_id
        if isinstance(job_id, Unset):
            raise ValueError(f"Cannot find the job_id for execution {execution_uid}")
        # Block until the job completes or fails
        job_response = poll_job_status(job_id)
        # Return the final job status and all available results
        # Regardless of the job status, we return all available results
        return job_response["state"], self.get_execution_result(execution_uid)

    @override
    def get_executions(self) -> List[Dict[str, Any]]:
        """Retrieves all executions for this prompt evaluator.

        This method fetches all executions that have been run using this evaluator.
        Executions are returned in chronological order, with the oldest execution first.

        The dictionary contains the following keys:

        - ``execution_uid``: The execution UID
        - ``created_at``: The timestamp when the execution was created
        - ``prompt_version_name``: The name of the prompt version used for the execution

        Example
        -------
        Example 1
        ^^^^^^^^^

        Get all executions for an evaluator:

        .. testcode::

            evaluator = PromptEvaluator.get(evaluator_uid=300)
            executions = evaluator.get_executions()
            for execution in executions:
                print(f"Execution {execution['execution_uid']}: {execution['created_at']}")
        """
        prompts = self._get_prompt_versions()

        executions: List[Dict[str, Any]] = []
        for prompt in prompts:
            executions.extend(
                {
                    "execution_uid": execution.prompt_execution_uid,
                    "created_at": execution.created_at,
                    "prompt_version_name": prompt.prompt_version_name,
                }
                for execution in prompt.executions
            )
        return sorted(executions, key=lambda x: x["created_at"])


@final
class CodeEvaluator(Evaluator):
    """
    An evaluator that uses custom Python code to assess an AI application's
    responses.

    A code evaluator uses custom Python functions to evaluate datapoints
    containing AI application responses, categorizing them into one of a
    criteria's labels by assigning the corresponding integer score and optional
    rationale. The evaluator function takes a datapoint as input and returns a
    score based on the criteria's label schema.

    The evaluation function can implement any Python logic needed to assess the
    AI application's response.

    Read more in the `Evaluation overview <https://docs.snorkel.ai/docs/user-guide/evaluation/evaluation-overview>`_.

    Using the ``CodeEvaluator`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import CodeEvaluator

    Examples
    --------
    Example 1
    ^^^^^^^^^

    Creates a new code evaluator, assessing the length of the AI application's
    response:

    .. code-block:: python

        import pandas as pd

        def evaluate(df: pd.DataFrame) -> pd.DataFrame:
            results = pd.DataFrame(index=df.index)
            results["score"] = df["response"].str.len() > 10  # Simple length check
            results["rationale"] = "Response length evaluation"
            return results

        # Create a new code evaluator
        evaluator = CodeEvaluator.create(
            criteria_uid=100,
            evaluate_function=evaluate,
            version_name="Version 1"
        )

    Example 2
    ^^^^^^^^^
    Gets an existing code evaluator:

    .. testcode::

        # Get existing evaluator
        evaluator = CodeEvaluator.get(
            evaluator_uid=300,
        )
    """

    # Note that we use a code-block in Example 1 because the evaluation function
    # name collides with other examples later in the file.
    # Wrapping the function definition in another function would work,
    # but would be more confusing for the documentation.

    @override
    @classmethod
    def get(cls, evaluator_uid: int) -> "CodeEvaluator":
        """Retrieves a code evaluator for a given uid.

        Parameters
        ----------
        evaluator_uid
            The unique identifier for the evaluator.

        Returns
        -------
        CodeEvaluator
            A CodeEvaluator instance.

        Raises
        ------
        ValueError
            If the evaluator with the given uid is not a CodeEvaluator.
        """
        evaluator = super().get(evaluator_uid)
        if not isinstance(evaluator, CodeEvaluator):
            raise ValueError(f"Evaluator {evaluator_uid} is not a CodeEvaluator")
        return evaluator

    @classmethod
    def create(
        cls,
        criteria_uid: int,
        evaluate_function: Callable[[pd.DataFrame], pd.DataFrame],
        version_name: Optional[str] = None,
    ) -> "CodeEvaluator":
        """Creates a new code evaluator for a criteria.

        Parameters
        ----------
        criteria_uid
            The unique identifier of the criteria that this evaluator assesses.
        evaluate_function
            A Python function that performs the evaluation. This function must:

            * Be named ``evaluate``
            * Accept a pandas DataFrame as input
            * Return a pandas DataFrame as output

            The input DataFrame has a MultiIndex with a single level named
            ``__DATAPOINT_UID`` that holds the unique identifier of the datapoint.
            Values in the index are of the form ``("uid1",)``.

            The output DataFrame must:

            * Have the same index as the input DataFrame
            * Include a column named ``score`` containing the evaluation results
            * Optionally include a column named ``rationale`` with explanations for the scores
        version_name
            The name for the initial code version. If not provided, a default name will be generated.

        Raises
        ------
        ValueError
            If the function name is not ``evaluate`` or if ``evaluate_function`` is not callable.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Creates a new code evaluator, assessing the length of the AI application's
        response:

        .. code-block:: python

            import pandas as pd

            def evaluate(df: pd.DataFrame) -> pd.DataFrame:
                results = pd.DataFrame(index=df.index)
                results["score"] = df["response"].str.len() > 10
                results["rationale"] = "Response length evaluation"
                return results

            evaluator = CodeEvaluator.create(
                criteria_uid=100,
                evaluate_function=evaluate,
            )
        """
        if evaluate_function is None:
            raise ValueError("evaluate_function must be provided")

        # Validate evaluate_function
        if not callable(evaluate_function):
            raise ValueError("evaluate_function must be a callable")

        if evaluate_function.__name__ != "evaluate":
            raise ValueError(
                f"Function name must be 'evaluate', got '{evaluate_function.__name__}'"
            )

        benchmark_uid = get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
            criteria_uid=criteria_uid,
        )

        response = create_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code_post(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            body=CreateOrUpdateCodePayload(
                code=dedent(inspect.getsource(evaluate_function)),
                code_version_name=_wrap_in_unset(version_name),
            ),
        )

        return cls(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            evaluator_uid=response.evaluator_uid,
        )

    @override
    def update(
        self,
        version_name: Optional[str] = None,
        evaluate_function: Optional[Callable[[pd.DataFrame], pd.DataFrame]] = None,
    ) -> None:
        """Updates the code evaluator with a new evaluation function.

        This method creates a new code version containing the provided evaluation
        function. The function must be declared with the name ``evaluate`` and
        will be used to assess datapoints containing AI application responses
        against the criteria.

        Parameters
        ----------
        version_name
            The name for the new code version. If not provided, a default name will be generated.
        evaluate_function
            A Python function that performs the evaluation. This function must:

            * Be named ``evaluate``
            * Accept a pandas DataFrame as input
            * Return a pandas DataFrame as output

            The input DataFrame has a MultiIndex with a single level named
            ``__DATAPOINT_UID`` that holds the unique identifier of the datapoint.
            Values in the index are of the form ``("uid1",)``.

            The output DataFrame must:

            * Have the same index as the input DataFrame
            * Include a column named ``score`` containing the evaluation results
            * Optionally include a column named ``rationale`` with explanations for the scores

        Raises
        ------
        ValueError
            If the function name is not 'evaluate' or if evaluate_function is not provided.

        Example
        -------

        Example 1
        ^^^^^^^^^

        Update a code evaluator with a new evaluation function:

        .. code-block:: python

            import pandas as pd

            def evaluate(df: pd.DataFrame) -> pd.DataFrame:
                results = pd.DataFrame(index=df.index)

                # Add random scores between 0 and 1
                results["score"] = np.random.randint(0, 3, size=len(df))

                # Add random rationales
                rationale_options = [
                    "This response is accurate and relevant.",
                    "The answer demonstrates good understanding.",
                    "Response shows appropriate reasoning.",
                    "This is a well-formed answer.",
                    "The content is factually correct.",
                ]
                results["rationale"] = np.random.choice(rationale_options, size=len(df))
                return results

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            version_name = evaluator.update("v2.0", evaluate_function=evaluate)
        """
        if evaluate_function is None:
            raise ValueError("evaluate_function must be provided")

        if not callable(evaluate_function):
            raise ValueError("evaluate_function must be a callable")

        # The above assertion is not sufficient for mypy to infer the type of the function
        # so we cast it to the proper type
        typed_evaluate_function = cast(
            Callable[[pd.DataFrame], pd.DataFrame], evaluate_function
        )

        if typed_evaluate_function.__name__ != "evaluate":
            raise ValueError(
                f"Function name must be 'evaluate', got '{typed_evaluate_function.__name__}'"
            )

        code = dedent(inspect.getsource(typed_evaluate_function))

        update_code_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__put(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
            body=CreateOrUpdateCodePayload(
                code=code,
                code_version_name=_wrap_in_unset(version_name),
            ),
        )

    @override
    def get_versions(self) -> List[str]:
        """Retrieves all code version names for this code evaluator.

        This method fetches all code version names that have been created for this
        evaluator. Versions are returned in chronological order, with the oldest
        version first.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Get all code version names for an evaluator:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            versions = evaluator.get_versions()
            for version in versions:
                print(f"Version: {version}")
        """
        response = list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
        )
        return [code_version.code_version_name for code_version in response]

    def _get_code_version_uid(self, version_name: str) -> int:
        """Gets the code version UID for a given version name.

        Parameters
        ----------
        version_name
            The name of the code version.

        Raises
        ------
        ValueError
            If the version name is not found.
        """
        response = list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
        )
        for code_version in response:
            if code_version.code_version_name == version_name:
                return code_version.code_version_uid
        raise ValueError(f"Code version '{version_name}' not found")

    @override
    def execute(
        self,
        split: str,
        num_rows: Optional[int] = None,
        version_name: Optional[str] = None,
        sync: bool = False,
    ) -> int:
        """Executes the code evaluator against a dataset split.

        This method runs the evaluation code against the specified dataset split.
        If no version name is specified, it uses the latest version.

        Parameters
        ----------
        split
            The dataset split to evaluate against (e.g., "train", "test", "validation").
        num_rows
            The number of rows to evaluate. If ``None``, evaluates all rows in the split.
        version_name
            The code version name to run. If ``None``, the latest code version is used.
        sync
            Whether to wait for the job to complete. If ``True``, blocks until completion.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Run the latest code version and poll for results:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            code_execution_uid = evaluator.execute(split="test", num_rows=100)
            status, results = evaluator.poll_execution_result(code_execution_uid, sync=False)

        Example 2
        ^^^^^^^^^

        Run a specific code version:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            code_execution_uid = evaluator.execute(
                split="test",
                num_rows=100,
                version_name="v1.0"
            )
        """
        if version_name is None:
            code_versions = self.get_versions()
            if not code_versions:
                raise ValueError("No code versions found for this evaluator")
            version_name = code_versions[-1]

        code_version_uid = self._get_code_version_uid(version_name)

        code_execution_response = (
            execute_code_version_code_version__code_version_uid__execute_post(
                code_version_uid=code_version_uid,
                body=ExecuteCodeVersionRequest(
                    code_version_uid=code_version_uid,
                    execution_vds_metadata=ExecutionVDSMetadata(
                        splits=[Splits(split)],
                        first_n_indexes=_wrap_in_unset(num_rows),
                    ),
                ),
            )
        )

        code_execution_uid = code_execution_response.code_execution.code_execution_uid
        job_uid = code_execution_response.code_execution.job_uid

        if isinstance(job_uid, Unset):
            # it's only typed as optional to allow for the case where the code execution is not yet started
            raise ValueError("job_uid should never be unset")

        if sync:
            poll_job_status(job_uid)

        return code_execution_uid

    @override
    def get_execution_result(
        self, execution_uid: int
    ) -> Dict[str, Dict[str, EvaluationScoreType]]:
        """Retrieves the evaluation results for a specific evaluation execution.

        This method reads the evaluation results from the database for the given
        evaluation execution UID.

        Parameters
        ----------
        execution_uid
            The evaluation execution UID to get results for.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Get the results of a code execution:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            code_execution_uid = evaluator.execute(split="test", num_rows=100)
            results = evaluator.get_execution_result(code_execution_uid)
            print(f"Evaluation scores: {results}")
        """
        # Direct API call with just the code_execution_uid
        results_response = (
            get_code_execution_results_code_execution__code_execution_uid__results_get(
                code_execution_uid=execution_uid,
            )
        )
        return results_response.results.to_dict()

    @override
    def poll_execution_result(
        self, execution_uid: int, sync: bool = False
    ) -> Tuple[str, Dict[str, Dict[str, EvaluationScoreType]]]:
        """Polls the job status and retrieves partial results.

        This method checks the current status of the evaluation job and returns
        both the job status and any available results. The current status
        can be ``running``, ``completed``, ``failed``, ``cancelled``, or ``unknown``.

        Parameters
        ----------
        execution_uid
            The code execution UID to poll for.
        sync
            Whether to wait for the job to complete. If ``False``, returns immediately
            with current status and partial results.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Poll for job status and partial results:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            code_execution_uid = evaluator.execute(split="test", num_rows=100)
            status, results = evaluator.poll_execution_result(code_execution_uid, sync=False)
            print(f"Job status: {status}")
            if results:
                print(f"Partial results: {results}")
        """
        # Get the code execution details to find the job_uid
        code_execution_response = (
            get_code_execution_code_execution__code_execution_uid__get(
                code_execution_uid=execution_uid,
            )
        )
        job_uid = code_execution_response.job_uid
        if isinstance(job_uid, Unset):
            # it's only typed as optional to allow for the case where the code execution is not yet started
            raise ValueError("job_uid should never be unset")

        # Block until the job is complete
        if sync:
            poll_job_status(job_uid)

        # Get job status
        job_response = get_job_for_uid_jobs__job_uid__get(job_uid=job_uid)
        job_status = job_response.state.value

        # Get current results (may be partial)
        try:
            results = self.get_execution_result(execution_uid)
        except ValueError:
            # Job might not have results yet
            results = {}

        return job_status, results

    @override
    def get_executions(self) -> List[Dict[str, Any]]:
        """Retrieves all executions for this code evaluator.

        This method fetches all executions that have been run using this evaluator.
        Executions are returned in chronological order, with the oldest execution first.

        The dictionary contains the following keys:

        - ``execution_uid``: The execution UID
        - ``created_at``: The timestamp when the execution was created
        - ``code_version_name``: The name of the code version used for the execution

        Example
        -------
        Example 1
        ^^^^^^^^^

        Get all executions for an evaluator:

        .. testcode::

            evaluator = CodeEvaluator.get(evaluator_uid=300)
            executions = evaluator.get_executions()
            for execution in executions:
                print(f"Execution {execution['execution_uid']}: {execution['created_at']}")
        """
        code_executions_response = list_code_executions_by_evaluator_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__executions_get(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
        )

        code_versions_response = list_code_versions_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_code__evaluator_uid__versions_get(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.criteria_uid,
            evaluator_uid=self.uid,
        )

        code_version_name_by_uid = {
            code_version.code_version_uid: code_version.code_version_name
            for code_version in code_versions_response
        }

        return [
            {
                "execution_uid": execution.code_execution_uid,
                "created_at": execution.created_at,
                "code_version_name": code_version_name_by_uid[
                    execution.code_version_uid
                ],
            }
            for execution in code_executions_response
        ]
