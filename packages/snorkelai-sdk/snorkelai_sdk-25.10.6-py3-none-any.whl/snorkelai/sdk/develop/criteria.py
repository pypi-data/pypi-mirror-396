from typing import Dict, Optional, final

from snorkelai.sdk.client_v3.tdm.api.benchmark import (
    get_benchmark_benchmarks__benchmark_uid__get,
)
from snorkelai.sdk.client_v3.tdm.api.criteria import (
    create_criteria_benchmarks__benchmark_uid__criteria_post,
    get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get,
    get_criteria_by_uid_benchmarks__benchmark_uid__criteria__criteria_uid__get,
    update_criteria_benchmarks__benchmark_uid__criteria__criteria_uid__put,
)
from snorkelai.sdk.client_v3.tdm.api.evaluator import (
    get_criteria_evaluators_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_get,
)
from snorkelai.sdk.client_v3.tdm.api.workflow import (
    get_workflow_by_id_workflows__workflow_uid__get,
)
from snorkelai.sdk.client_v3.tdm.models.create_criteria_payload import (
    CreateCriteriaPayload,
)
from snorkelai.sdk.client_v3.tdm.models.create_criteria_payload_label_ordinality_by_user_label import (
    CreateCriteriaPayloadLabelOrdinalityByUserLabel,
)
from snorkelai.sdk.client_v3.tdm.models.create_criteria_payload_raw_label_by_user_label import (
    CreateCriteriaPayloadRawLabelByUserLabel,
)
from snorkelai.sdk.client_v3.tdm.models.criteria import Criteria as CriteriaApiModel
from snorkelai.sdk.client_v3.tdm.models.criteria_state import CriteriaState
from snorkelai.sdk.client_v3.tdm.models.update_criteria_payload import (
    UpdateCriteriaPayload,
)
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.develop.evaluators import Evaluator


@final
class Criteria(Base):
    """
    A criteria represents a specific characteristic or feature being evaluated
    as part of a benchmark.

    Criteria define what aspects of a model or AI application's performance are
    being measured, such as accuracy, relevance, safety, and other qualities.
    Each criteria is associated with a benchmark and has an evaluator that
    assesses whether a model's output satisfies that criteria.

    The heart of each criteria is its associated label schema, which defines
    what, exactly, the criteria is measuring, and maps each option to an
    integer.

    For example, a criteria that measures accuracy might have a label schema
    that defines the following labels:

    * ``INCORRECT``: 0
    * ``CORRECT``: 1

    A criteria that measures readability might have a label schema that defines
    the following labels:

    * ``POOR``: 0
    * ``ACCEPTABLE``: 1
    * ``EXCELLENT``: 2

    Read more in the `Evaluation overview <https://docs.snorkel.ai/docs/user-guide/evaluation/evaluation-overview>`_.
    """

    _benchmark_uid: int
    _criteria_uid: int
    _name: str
    _metric_label_schema_uid: int
    _description: Optional[str] = None
    _rationale_label_schema_uid: Optional[int] = None
    _archived: bool = False

    def __init__(
        self,
        benchmark_uid: int,
        criteria_uid: int,
        name: str,
        metric_label_schema_uid: int,
        description: Optional[str] = None,
        rationale_label_schema_uid: Optional[int] = None,
        archived: bool = False,
    ):
        """
        Parameters
        ----------
        benchmark_uid
            The unique identifier of the parent Benchmark. The ``benchmark_uid`` is
            visible in the URL of the benchmark page in the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.
        criteria_uid
            The unique identifier for this criteria.
        name
            The name of the criteria.
        metric_label_schema_uid
            The ID of the schema defining the metric labels.
        description
            A detailed description of what the criteria measures.
        rationale_label_schema_uid
            The ID of the schema defining rationale labels (if applicable).
        archived
            Whether the criteria is archived.

        Examples
        --------
        Using the ``Criteria`` class requires the following import:

        .. testcode::

            from snorkelai.sdk.develop import Criteria

        Create a new criteria:

        .. testcode::

            # Create a new criteria
            criteria = Criteria.create(
                benchmark_uid=100,
                name="Accuracy",
                description="Measures response accuracy",
                label_map={"Correct": 1, "Incorrect": 0},
                requires_rationale=True
            )

        Get an existing criteria:

        .. testcode::

            # Get existing criteria
            criteria = Criteria.get(criteria_uid=100)
        """
        self._benchmark_uid = benchmark_uid
        self._criteria_uid = criteria_uid
        self._name = name
        self._metric_label_schema_uid = metric_label_schema_uid
        self._description = description
        self._rationale_label_schema_uid = rationale_label_schema_uid
        self._archived = archived

    @property
    def uid(self) -> int:
        """Return the UID of the criteria"""
        return self._criteria_uid

    @property
    def criteria_uid(self) -> int:
        """Return the UID of the criteria"""
        # This is only for backcompat
        return self._criteria_uid

    @property
    def benchmark_uid(self) -> int:
        """Return the UID of the parent benchmark"""
        return self._benchmark_uid

    @property
    def name(self) -> str:
        """Return the name of the criteria"""
        return self._name

    @property
    def metric_label_schema_uid(self) -> int:
        """Return the UID of the metric label schema"""
        return self._metric_label_schema_uid

    @property
    def description(self) -> Optional[str]:
        """Return the description of the criteria"""
        return self._description

    @property
    def rationale_label_schema_uid(self) -> Optional[int]:
        """Return the UID of the rationale label schema"""
        return self._rationale_label_schema_uid

    @property
    def archived(self) -> bool:
        """Return whether the criteria is archived"""
        return self._archived

    @staticmethod
    def _from_response_model(criteria_response: CriteriaApiModel) -> "Criteria":
        """Converts a response model from the API to a Criteria object. Intended for internal use only.

        Parameters
        ----------
        criteria_response
            The response model from the API.
        """
        response_dict = criteria_response.to_dict()
        return Criteria(
            benchmark_uid=response_dict["benchmark_uid"],
            criteria_uid=response_dict["criteria_uid"],
            name=response_dict["name"],
            metric_label_schema_uid=response_dict["output_format"][
                "metric_label_schema_uid"
            ],
            description=response_dict.get("description"),
            rationale_label_schema_uid=response_dict["output_format"].get(
                "rationale_label_schema_uid"
            ),
            archived=response_dict["state"] == CriteriaState.ARCHIVED,
        )

    @staticmethod
    def create(
        benchmark_uid: int,
        name: str,
        label_map: Dict[str, int],
        description: Optional[str] = None,
        requires_rationale: bool = False,
    ) -> "Criteria":
        """Create a new criteria for a benchmark.

        Your ``label_map`` must use consecutive integers starting from ``0``.
        For example, if you have three labels, you must use the values ``0``,
        ``1``, and ``2``.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the parent Benchmark.
        name
            The name of the criteria.
        label_map
            A dictionary mapping user-friendly labels to numeric values.
            The key "UNKNOWN" will always be added with value -1.
            Dictionary values must be consecutive integers starting from 0.
        description
            A detailed description of what the criteria measures.
        requires_rationale
            Whether the criteria requires rationale.

        Returns
        -------
        Criteria
            A new Criteria object representing the created criteria.

        Raises
        ------
        ValueError
            If label_map is empty or has invalid values.

        Example
        -------
        .. testcode::

            criteria = Criteria.create(
                benchmark_uid=200,
                name="Accuracy",
                description="Measures response accuracy",
                label_map={"Correct": 1, "Incorrect": 0},
                requires_rationale=True
            )
        """
        if not label_map:
            raise ValueError("Label map must be non-empty")

        non_unknown_values = [v for k, v in label_map.items() if k != "UNKNOWN"]
        if sorted(non_unknown_values) != list(range(len(non_unknown_values))):
            raise ValueError(
                "Label values must be consecutive integers starting from 0"
            )

        # Create the criteria
        raw_label_by_user_label = label_map.copy()
        raw_label_by_user_label["UNKNOWN"] = -1

        benchmark = get_benchmark_benchmarks__benchmark_uid__get(benchmark_uid)
        workflow = get_workflow_by_id_workflows__workflow_uid__get(
            benchmark.workflow_uid
        )
        dataset_uid = workflow.input_dataset_uid
        if type(dataset_uid) is not int:
            raise ValueError(
                f"Benchmark {benchmark_uid} does not have an input dataset"
            )

        response = create_criteria_benchmarks__benchmark_uid__criteria_post(
            benchmark_uid=benchmark_uid,
            body=CreateCriteriaPayload(
                benchmark_uid=benchmark_uid,
                dataset_uid=dataset_uid,
                name=name,
                description=description if description is not None else UNSET,
                requires_rationale=requires_rationale,
                raw_label_by_user_label=CreateCriteriaPayloadRawLabelByUserLabel.from_dict(
                    raw_label_by_user_label,
                ),
                label_ordinality_by_user_label=CreateCriteriaPayloadLabelOrdinalityByUserLabel.from_dict(
                    raw_label_by_user_label,
                ),
            ),
        )

        return Criteria._from_response_model(response)

    @staticmethod
    def get(criteria_uid: int) -> "Criteria":
        """Get an existing criteria by its UID.

        Parameters
        ----------
        criteria_uid
            The unique identifier for the criteria.

        Returns
        -------
        Criteria
            A Criteria object representing the existing criteria.

        Raises
        ------
        ValueError
            If the criteria is not found.

        Example
        -------
        .. testcode::

            criteria = Criteria.get(criteria_uid=100)
        """
        benchmark_uid = get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get(
            criteria_uid=criteria_uid,
        )

        response = (
            get_criteria_by_uid_benchmarks__benchmark_uid__criteria__criteria_uid__get(
                benchmark_uid=benchmark_uid,
                criteria_uid=criteria_uid,
            )
        )

        return Criteria._from_response_model(response)

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> None:
        """Updates the criteria with the given parameters. If a parameter
        is not provided or is None, the existing value will be left unchanged.

        Parameters
        ----------
        name
            The name of the criteria.
        description
            A detailed description of what the criteria measures.
        archived
            Whether the criteria is archived.

        Example
        -------
        .. testcode::

            criteria = Criteria.get(criteria_uid=100)
            criteria.update(name="New Name", description="New description")
        """
        criteria_response = (
            update_criteria_benchmarks__benchmark_uid__criteria__criteria_uid__put(
                benchmark_uid=self.benchmark_uid,
                criteria_uid=self.uid,
                body=UpdateCriteriaPayload(
                    name=name if name else UNSET,
                    description=description if description else UNSET,
                    state=(
                        UNSET
                        if archived is None
                        else (
                            CriteriaState.ARCHIVED if archived else CriteriaState.ACTIVE
                        )
                    ),
                ),
            )
        )

        new_obj = Criteria._from_response_model(criteria_response)
        self.__dict__.update(new_obj.__dict__)

    def archive(self) -> None:
        """Archives the criteria, hiding it from the UI and Benchmark.list_criteria method.

        Use :meth:`snorkelai.sdk.develop.benchmarks.Benchmark.list_criteria` with
        ``include_archived=True`` to view archived criteria.
        """
        self.update(archived=True)

    def get_evaluator(self) -> Evaluator:
        """Retrieves the evaluator associated with this criteria.

        An evaluator is a prompt or code snippet that assesses whether a model's output
        satisfies the criteria. Each criteria has one evaluator that assesses
        each datapoint against the criteria's label schema and chooses the most
        appropriate label, in the form of the associated integer.

        The evaluator can be either a code evaluator (using custom Python functions)
        or a prompt evaluator (using LLM prompts).

        Raises
        ------
        IndexError
            If no evaluator is found for this criteria.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Get the evaluator for a criteria and check its type:

        .. testcode::

            from snorkelai.sdk.develop import PromptEvaluator, CodeEvaluator

            criteria = Criteria.get(criteria_uid=100)
            evaluator = criteria.get_evaluator()

            if isinstance(evaluator, CodeEvaluator):
                print("This is a code evaluator")
            elif isinstance(evaluator, PromptEvaluator):
                print("This is a prompt evaluator")
        """
        response = get_criteria_evaluators_benchmarks__benchmark_uid__criteria__criteria_uid__evaluators_get(
            benchmark_uid=self.benchmark_uid,
            criteria_uid=self.uid,
        )
        # Currently, there is only one evaluator per criteria, so we can just use the first one
        return Evaluator._from_api_model(self.benchmark_uid, response[0])

    @classmethod
    def delete(cls, criteria_uid: int) -> None:
        """Deletion of a criteria is not implemented.

        Parameters
        ----------
        criteria_uid
            The unique identifier of the criteria.
        """
        raise NotImplementedError("Not implemented")
