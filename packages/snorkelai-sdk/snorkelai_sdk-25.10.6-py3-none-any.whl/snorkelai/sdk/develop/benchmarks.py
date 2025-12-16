import json
import os
import sys
from datetime import datetime
from typing import List, Optional, final

from snorkelai.sdk.client_v3.tdm.api.workflow import (
    get_workflow_by_id_workflows__workflow_uid__get,
)

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from snorkelai.sdk.client import SnorkelSDKContext
from snorkelai.sdk.client_v3.tdm.api.benchmark import (
    create_benchmark_benchmarks_post,
    create_benchmark_execution_benchmarks__benchmark_uid__executions_post,
    export_benchmark_config_benchmarks__benchmark_uid__export_config_get,
    get_benchmark_benchmarks__benchmark_uid__get,
    get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get,
    list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get,
    update_benchmark_benchmarks__benchmark_uid__put,
)
from snorkelai.sdk.client_v3.tdm.api.criteria import (
    get_criteria_for_benchmark_benchmarks__benchmark_uid__criteria_get,
)
from snorkelai.sdk.client_v3.tdm.models.benchmark import Benchmark as BenchmarkApiModel
from snorkelai.sdk.client_v3.tdm.models.create_benchmark_execution_payload import (
    CreateBenchmarkExecutionPayload,
)
from snorkelai.sdk.client_v3.tdm.models.create_benchmark_payload import (
    CreateBenchmarkPayload,
)
from snorkelai.sdk.client_v3.tdm.models.update_benchmark_payload import (
    UpdateBenchmarkPayload,
)
from snorkelai.sdk.client_v3.tdm.models.workflow_state import WorkflowState
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import get_workspace_uid
from snorkelai.sdk.context.ctx import DEFAULT_WORKSPACE_UID
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.develop.benchmark_executions import (
    BenchmarkExecution,
    BenchmarkExecutionExportConfig,
)
from snorkelai.sdk.develop.criteria import Criteria


class BenchmarkExportFormat(StrEnum):
    JSON = "json"


@final
class Benchmark(Base):
    """
    A benchmark is the collection of characteristics that you care about for a
    particular GenAI application, and the measurements you use to assess the
    performance against those characteristics. It consists of the following elements:

    - **Reference prompts:** A set of prompts used to evaluate the model's responses.
    - **Slices:** Subsets of reference prompts focusing on specific topics.
    - **Criteria:** Key characteristics that represent the features being optimized for evaluation.
    - **Evaluators:** Functions that assess whether a model's output satisfies the criteria.

    Read more in the `Evaluation overview <https://docs.snorkel.ai/docs/user-guide/evaluation/evaluation-overview>`_.

    Using the ``Benchmark`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import Benchmark
    """

    _benchmark_uid: int
    _name: str
    _created_at: datetime
    _updated_at: datetime
    _archived: bool
    _description: Optional[str] = None

    def __init__(
        self,
        benchmark_uid: int,
        name: str,
        created_at: datetime,
        updated_at: datetime,
        archived: bool,
        description: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark from which you want to
            get data. The ``benchmark_uid`` is visible in the URL of the benchmark
            page in the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.
        name
            The name of the benchmark.
        description
            The description of the benchmark.
        created_at
            The timestamp when the benchmark was created.
        updated_at
            The timestamp when the benchmark was last updated.
        archived
            Whether the benchmark is archived.
        """
        self._benchmark_uid = benchmark_uid
        self._name = name
        self._created_at = created_at
        self._updated_at = updated_at
        self._archived = archived
        self._description = description

    @property
    def uid(self) -> int:
        """Return the UID of the benchmark"""
        return self._benchmark_uid

    @property
    def benchmark_uid(self) -> int:
        """Return the UID of the benchmark"""
        # This is only for backcompat
        return self._benchmark_uid

    @property
    def name(self) -> str:
        """Return the name of the benchmark"""
        return self._name

    @property
    def created_at(self) -> datetime:
        """Return the timestamp when the benchmark was created"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Return the timestamp when the benchmark was last updated"""
        return self._updated_at

    @property
    def archived(self) -> bool:
        """Return whether the benchmark is archived"""
        return self._archived

    @property
    def description(self) -> Optional[str]:
        """Return the description of the benchmark"""
        return self._description

    @staticmethod
    def _from_response_model(benchmark_response: BenchmarkApiModel) -> "Benchmark":
        """Converts a response dictionary from the API to a Benchmark object. Intended for internal use only.

        Parameters
        ----------
        benchmark_response
            The response dictionary from the API.
        """
        response_dict = benchmark_response.to_dict()
        return Benchmark(
            benchmark_uid=response_dict["benchmark_uid"],
            name=response_dict["name"],
            created_at=datetime.fromisoformat(response_dict["created_at"]),
            updated_at=datetime.fromisoformat(response_dict["updated_at"]),
            archived=response_dict["workflow_state"] == WorkflowState.ARCHIVED,
            description=response_dict.get("description"),
        )

    @staticmethod
    def create(
        name: str,
        dataset_uid: int,
        description: Optional[str] = None,
    ) -> "Benchmark":
        """Creates a new benchmark. The created benchmark does not include any default criteria or evaluators.

        Parameters
        ----------
        name
            The name of the benchmark.
        dataset_uid
            The unique identifier of the dataset to use as the input for the benchmark. The ``dataset_uid`` can be retrieved using the
            :meth:`snorkelai.sdk.develop.datasets.Dataset.list` method.
        description
            The description of the benchmark.

        Returns
        -------
        Benchmark
            A Benchmark object representing the created benchmark.
        """
        workspace_name = SnorkelSDKContext.get_global().workspace_name
        workspace_uid = (
            DEFAULT_WORKSPACE_UID
            if workspace_name is None
            else get_workspace_uid(workspace_name)
        )

        response = create_benchmark_benchmarks_post(
            body=CreateBenchmarkPayload(
                name=name,
                description=description if description is not None else UNSET,
                workspace_uid=workspace_uid,
                input_dataset_uid=dataset_uid,
            )
        )
        return Benchmark._from_response_model(response)

    @staticmethod
    def get(benchmark_uid: int) -> "Benchmark":
        """Gets a benchmark by its unique identifier.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark from which you want to
            get data. The ``benchmark_uid`` is visible in the URL of the benchmark
            page in the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.

        Returns
        -------
        Benchmark
            A Benchmark object representing the benchmark with the given ``benchmark_uid``.

        """
        response = get_benchmark_benchmarks__benchmark_uid__get(
            benchmark_uid=benchmark_uid
        )

        return Benchmark._from_response_model(response)

    @staticmethod
    def list(workspace_uid: int, include_archived: bool = False) -> List["Benchmark"]:
        """Lists all benchmarks for a given workspace.

        Parameters
        ----------
        workspace_uid
            The unique identifier of the workspace from which you want to
            list benchmarks. The ``workspace_uid`` can be retrieved using the
            :meth:`snorkelai.sdk.client_v3.utils.get_workspace_uid` method.
        include_archived
            Whether to include archived benchmarks.

        Returns
        -------
        List[Benchmark]
            A list of Benchmark objects representing all benchmarks in the given workspace.
        """
        response = get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get(
            workspace_uid=workspace_uid, include_archived=include_archived
        )

        return [Benchmark._from_response_model(benchmark) for benchmark in response]

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        archived: Optional[bool] = None,
    ) -> None:
        """Updates the benchmark with the given parameters. If a parameter
        is not provided or is None, the existing value will be left unchanged.

        Parameters
        ----------
        name
            The new name of the benchmark.
        description
            The new description of the benchmark.
        archived
            Whether the benchmark should be archived.

        Example
        -------
        .. testcode::

            benchmark = Benchmark.get(100)
            benchmark.update(name="New Name", description="New description")
        """
        response = update_benchmark_benchmarks__benchmark_uid__put(
            benchmark_uid=self.uid,
            body=UpdateBenchmarkPayload(
                name=name if name is not None else UNSET,
                description=description if description is not None else UNSET,
                state=(
                    UNSET
                    if archived is None
                    else WorkflowState.ARCHIVED if archived else WorkflowState.ACTIVE
                ),
            ),
        )

        new_obj = Benchmark._from_response_model(response)
        self.__dict__.update(new_obj.__dict__)

    def archive(self) -> None:
        """Archives the benchmark, hiding it from the UI and SDK list method.

        Use :meth:`snorkelai.sdk.develop.benchmarks.Benchmark.list` with
        ``include_archived=True`` to view archived benchmarks.
        """
        self.update(archived=True)

    def list_criteria(self, include_archived: bool = False) -> List[Criteria]:
        """Retrieves all criteria for this benchmark.

        Criteria are the key characteristics that represent the features being optimized
        for evaluation. Each criteria defines what aspect of the model's performance
        is being measured, such as accuracy, relevance, or safety.

        Each Criteria object contains:

        - criteria_uid: The unique identifier for this criteria.
        - benchmark_uid: The ID of the parent benchmark.
        - name: The name of the criteria.
        - description: A detailed description of what the criteria measures.
        - requires_rationale: Whether the criteria requires a rationale explanation.
        - label_map: A dictionary mapping user-friendly labels to numeric values.

        Parameters
        ----------
        include_archived
            Whether to include archived criteria.

        Returns
        -------
        List[Criteria]
            A list of Criteria objects representing all criteria in this benchmark.

        Example
        -------

        Example 1
        ^^^^^^^^^

        Get all criteria for a benchmark and list them:

        .. testcode::

            benchmark = Benchmark.get(100)
            criteria_list = benchmark.list_criteria()
            for criteria in criteria_list:
                print(f"Criteria: {criteria.name} - {criteria.description}")
        """
        response = get_criteria_for_benchmark_benchmarks__benchmark_uid__criteria_get(
            benchmark_uid=self.uid,
            include_archived=include_archived,
        )

        return [Criteria._from_response_model(criteria) for criteria in response]

    def list_executions(
        self, include_archived: bool = False
    ) -> List[BenchmarkExecution]:
        """Retrieves all benchmark executions for this benchmark.

        A benchmark execution represents a single run of a benchmark against a dataset,
        capturing the results and metadata of that evaluation. Executions are returned
        in chronological order, with the most recent execution last.

        Each BenchmarkExecution object contains:

        - benchmark_uid: The ID of the parent benchmark.
        - benchmark_execution_uid: The unique identifier for this execution.
        - name: The name of the execution.
        - created_at: Timestamp when the execution was created.
        - created_by: Username of the execution creator.
        - archived: Whether the execution is archived.

        After retrieving executions, you can export their results using
        :meth:`export_latest_execution` or export the benchmark configuration
        using :meth:`export_config`. For more information about exporting
        benchmarks, see `Export evaluation benchmark
        <https://docs.snorkel.ai/docs/user-guide/evaluation/export-benchmark>`_.

        Parameters
        ----------
        include_archived
            Whether to include archived executions.

        Returns
        -------
        List[BenchmarkExecution]

        Example
        -------

        Example 1
        ^^^^^^^^^

        Get all executions for a benchmark and list them:

        .. testcode::

            benchmark = Benchmark.get(100)
            executions = benchmark.list_executions()
        """
        # The sort order is guaranteed by the route.
        return [
            BenchmarkExecution._from_response_model(execution, benchmark_uid=self.uid)
            for execution in list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
                benchmark_uid=self.uid,
                include_archived=include_archived,
            )
        ]

    def export_config(
        self,
        filepath: str,
        format: BenchmarkExportFormat = BenchmarkExportFormat.JSON,
    ) -> None:
        """
        Exports a benchmark configuration to the specified format and writes to the provided filepath.

        This method exports the complete benchmark configuration, including all criteria,
        evaluators, and metadata. The exported configuration can be used for:

        - Version control of benchmark definitions.
        - Sharing benchmarks across teams.
        - Integration with CI/CD pipelines.
        - Backing up evaluation configurations.

        Parameters
        ----------
        filepath
            Output file path for exported data. The directory will be created
            if it doesn't exist.
        format
            The format to export the config to. Currently only JSON is supported.

        Raises
        ------
        NotImplementedError
            If an unsupported export format is specified.
        ValueError
            If the benchmark_uid is None or invalid.

        Example
        -------
        Example 1
        ^^^^^^^^^

        Export a benchmark configuration to JSON:

        .. testcode::

            benchmark = Benchmark.get(100)
            benchmark.export_config("benchmark_config.json")

        Example 1 output
        ^^^^^^^^^^^^^^^^

        The exported JSON file contains:

        .. code-block:: JSON

            {
              "criteria": [
                {
                  "criteria_uid": 101,
                  "benchmark_uid": 100,
                  "name": "Example Readability",
                  "description": "Evaluates how easy the response is to read and understand.",
                  "state": "ACTIVE",
                  "output_format": {
                    "metric_label_schema_uid": 200,
                    "rationale_label_schema_uid": 201
                  },
                  "metadata": {
                    "version": "1.0"
                  },
                  "created_at": "2025-04-01T14:30:00.123456Z",
                  "updated_at": "2025-04-01T14:35:10.654321Z"
                }
              ],
              "evaluators": [
                {
                  "evaluator_uid": 301,
                  "name": "Readability Evaluator (LLM)",
                  "description": "Uses an LLM prompt to assess readability.",
                  "criteria_uid": 101,
                  "type": "Prompt",
                  "prompt_workflow_uid": 401,
                  "parameters": null,
                  "metadata": {
                    "default_prompt_config": {
                      "name": "Readability Prompt v1",
                      "model_name": "google/gemini-1.5-pro-latest",
                      "system_prompt": "You are an expert evaluator assessing text readability.",
                      "user_prompt": "..."
                    }
                  },
                  "created_at": "2025-04-01T15:00:00.987654Z",
                  "updated_at": "2025-04-01T15:05:00.123123Z"
                }
              ],
              "metadata": {
                "name": "Sample Benchmark Set",
                "description": "A benchmark set including example evaluations.",
                "created_at": "2025-04-01T14:00:00.000000Z",
                "created_by": "user@example.com"
              }
                        }

        After exporting your benchmark, you can use it to evaluate data from your GenAI
        application iteratively, allowing you to measure and refine your LLM system.
        """
        if format != BenchmarkExportFormat.JSON:
            raise NotImplementedError(f"Unsupported export format: {format}")

        config = export_benchmark_config_benchmarks__benchmark_uid__export_config_get(
            benchmark_uid=self.uid
        )

        os.makedirs(os.path.dirname(os.path.abspath(filepath)) or ".", exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(config.to_dict(), f, indent=2)

        print(f"Benchmark config exported to {filepath}")

    def export_latest_execution(
        self,
        filepath: str,
        # Note we use None as the default value so that it renders well in the docs.
        # Providing JsonExportConfig() doesn't look nice in the docs.
        config: Optional[BenchmarkExecutionExportConfig] = None,
    ) -> None:
        """Export the latest benchmark execution with all its associated data.

        This method exports the most recent benchmark execution, including all evaluation
        results and metadata. The exported dataset contains:

        * Benchmark metadata for the associated benchmark
        * Execution metadata for this execution
        * Each datapoint lists its evaluation score, which includes:
            * The evaluator outputs
            * Rationale
            * Agreement with ground truth
        * Each datapoint lists its slice membership(s)
        * (CSV exports only) Uploaded user columns and ground truth

        The export includes all datapoints without filtering or sampling.
        Some datapoints may have missing evaluation scores if the benchmark was
        not executed against them (for example, datapoints in the test split).

        Parameters
        ----------
        filepath
            Output file path for exported data.
        config
            A ``JsonExportConfig`` or ``CsvExportConfig`` object. If not provided, JSON will be used by default.
            No additional configuration is required for JSON exports. For CSV exports, the following parameters are supported:

            * ``sep``: The separator between columns. Default: ``,``.
            * ``quotechar``: The character used to quote fields. Default: ``"``.
            * ``escapechar``: The character used to escape special characters. Default: ``\\``.


        Example
        -------

        Example 1
        ^^^^^^^^^

        Export the latest benchmark execution to JSON:

        .. testcode::

            benchmark = Benchmark.get(100)
            benchmark.export_latest_execution("benchmark_execution.json")

        Example 1 return
        ^^^^^^^^^^^^^^^^

        The exported JSON file contains:

        .. code-block:: JSON

            {
                "benchmark_metadata": {
                    "uid": 100,
                    "name": "Example Benchmark",
                    "description": "A benchmark for testing model performance",
                    "created_at": "2025-01-01T12:00:00Z",
                    "created_by": "user@example.com"
                },
                "execution_metadata": {
                    "uid": 1,
                    "name": "Latest Run",
                    "created_at": "2025-01-01T12:00:00Z",
                    "created_by": "user@example.com"
                },
                "data": [
                    {
                        "x_uid": "doc::0",
                        "scores": [
                           {
                                "criteria_uid": 101,
                                "criteria_name": "Readability",
                                "score_type": "RATIONALE",
                                "value": "The response is clear and well-structured",
                                "error": ""
                           },
                           {
                                "criteria_uid": 101,
                                "criteria_name": "Readability",
                                "score_type": "EVAL",
                                "value": 0.85,
                            },
                            {
                                "criteria_uid": 101,
                                "criteria_name": "Readability",
                                "score_type": "AGREEMENT",
                                "value": 1.0
                            }
                        ],
                        "slice_membership": ["test_set"]
                    },
                    {
                        "x_uid": "doc::1",
                        "scores": [
                            {
                                "criteria_uid": 101,
                                "criteria_name": "Readability",
                                "score_type": "EVAL",
                                "value": 0.92,
                            }
                        ],
                        "slice_membership": ["test_set"]
                    }
                ],
                "slices": [
                    {
                        "id": "None",
                        "display_name": "All Datapoints",
                        "reserved_slice_type": "global"
                    },
                    {
                        "id": "-1",
                        "display_name": "No Slice",
                        "reserved_slice_type": "no_slice"
                    },
                    {
                        "id": "5",
                        "display_name": "Your Slice",
                        "reserved_slice_type": "regular_slice"
                    }
                ]
            }
        """
        execution = self.list_executions()[-1]
        execution.export(filepath, config)

    def execute(
        self,
        splits: Optional[List[str]] = None,
        criteria_uids: Optional[List[int]] = None,
        name: Optional[str] = None,
    ) -> BenchmarkExecution:
        """Executes the benchmark against the associated dataset.
        For each criteria, evaluation scores are computed for each datapoint and aggregate metrics are computed across all datapoints.

        Parameters
        ----------
        splits
            The splits to execute the benchmark on. If not provided, will default to ["train", "valid"].
        criteria_uids
            The criteria to execute the benchmark on. If not provided, will default to all criteria for the benchmark.
        name
            The name of the execution. If not provided, will default to "Run <number>" based on the number of previous executions.

        Returns
        -------
        BenchmarkExecution
            The execution object.
        """
        benchmark = get_benchmark_benchmarks__benchmark_uid__get(self.uid)
        workflow = get_workflow_by_id_workflows__workflow_uid__get(
            benchmark.workflow_uid
        )
        dataset_uid = workflow.input_dataset_uid

        if type(dataset_uid) is not int:
            raise ValueError(f"Benchmark {self.uid} does not have an input dataset")
        response = (
            create_benchmark_execution_benchmarks__benchmark_uid__executions_post(
                benchmark_uid=self.uid,
                body=CreateBenchmarkExecutionPayload(
                    dataset_uid=dataset_uid,
                    splits=splits if splits is not None else UNSET,
                    criteria_uids=criteria_uids if criteria_uids is not None else UNSET,
                    name=name if name is not None else UNSET,
                ),
            )
        )
        return BenchmarkExecution._from_response_model(response)

    @classmethod
    def delete(cls, benchmark_uid: int) -> None:
        """Deletion of a benchmark is not implemented.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark.
        """
        raise NotImplementedError("Not implemented")
