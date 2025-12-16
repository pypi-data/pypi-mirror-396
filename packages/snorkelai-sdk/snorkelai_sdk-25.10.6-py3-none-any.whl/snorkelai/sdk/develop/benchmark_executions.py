import sys
from datetime import datetime
from typing import List, Optional, Union, final, overload

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from snorkelai.sdk.client_v3.tdm.api.benchmark import (
    create_benchmark_execution_benchmarks__benchmark_uid__executions_post,
    get_benchmark_benchmarks__benchmark_uid__get,
    list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get,
)
from snorkelai.sdk.client_v3.tdm.api.execution import (
    export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get,
    update_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__put,
)
from snorkelai.sdk.client_v3.tdm.api.workflow import (
    get_workflow_by_id_workflows__workflow_uid__get,
)
from snorkelai.sdk.client_v3.tdm.models.benchmark_execution import (
    BenchmarkExecution as BenchmarkExecutionApiModel,
)
from snorkelai.sdk.client_v3.tdm.models.benchmark_execution_export_metadata import (
    BenchmarkExecutionExportMetadata,
)
from snorkelai.sdk.client_v3.tdm.models.benchmark_execution_state import (
    BenchmarkExecutionState,
)
from snorkelai.sdk.client_v3.tdm.models.create_benchmark_execution_payload import (
    CreateBenchmarkExecutionPayload,
)
from snorkelai.sdk.client_v3.tdm.models.update_benchmark_execution_payload import (
    UpdateBenchmarkExecutionPayload,
)
from snorkelai.sdk.client_v3.utils import _wrap_in_unset
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.utils.export_helpers import download_to_file


class BenchmarkExecutionExportFormat(StrEnum):
    JSON = "json"
    CSV = "csv"


class JsonExportConfig:
    """Benchmark execution JSON export configuration"""

    def __init__(self) -> None:
        """
        Parameters
        ----------
        """
        self.format = BenchmarkExecutionExportFormat.JSON


class CsvExportConfig:
    """Benchmark execution CSV export configuration"""

    def __init__(
        self,
        sep: str = ",",
        quotechar: str = '"',
        escapechar: str = "\\",
    ):
        """
        Parameters
        ----------
        sep
            The separator between columns.
        quotechar
            The character used to quote fields.
        escapechar
            The character used to escape special characters.
        """
        self.format = BenchmarkExecutionExportFormat.CSV
        self.sep = sep
        self.quotechar = quotechar
        self.escapechar = escapechar


BenchmarkExecutionExportConfig = Union[JsonExportConfig, CsvExportConfig]


@final
class BenchmarkExecution(Base):
    """
    Represents a single execution run of a benchmark for a dataset.

    A benchmark execution exports comprehensive evaluation data including
    per-datapoint scores (evaluator outputs, rationales, and ground truth
    agreement), slice membership, benchmark and execution metadata, including
    timing information and execution context.
    """

    _benchmark_uid: int
    _benchmark_execution_uid: int
    _name: str
    _created_at: datetime
    _created_by: str
    _archived: bool

    def __init__(
        self,
        benchmark_uid: int,
        benchmark_execution_uid: int,
        name: str,
        created_at: datetime,
        created_by: str,
        archived: bool,
    ):
        """
        Parameters
        ----------
        benchmark_uid
            The unique identifier of the parent Benchmark. The ``benchmark_uid`` is
            visible in the URL of the benchmark page in the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.
        benchmark_execution_uid
            The unique identifier for this execution.
        name
            The name of the execution.
        created_at
            Timestamp of when this execution was run.
        created_by
            Username of the user who ran this execution.
        archived
            Whether this execution is archived.
        """
        self._benchmark_uid = benchmark_uid
        self._benchmark_execution_uid = benchmark_execution_uid
        self._name = name
        self._created_at = created_at
        self._created_by = created_by
        self._archived = archived

    @property
    def uid(self) -> int:
        """Return the UID of the benchmark execution"""
        return self._benchmark_execution_uid

    @property
    def benchmark_execution_uid(self) -> int:
        """Return the UID of the benchmark execution"""
        # This is only for backcompat
        return self._benchmark_execution_uid

    @property
    def benchmark_uid(self) -> int:
        """Return the UID of the parent benchmark"""
        return self._benchmark_uid

    @property
    def name(self) -> str:
        """Return the name of the benchmark execution"""
        return self._name

    @property
    def created_at(self) -> datetime:
        """Return the timestamp when the benchmark execution was created"""
        return self._created_at

    @property
    def created_by(self) -> str:
        """Return the username of the user who created the benchmark execution"""
        return self._created_by

    @property
    def archived(self) -> bool:
        """Return whether the benchmark execution is archived"""
        return self._archived

    @overload
    @staticmethod
    def _from_response_model(
        benchmark_execution_response: BenchmarkExecutionApiModel,
    ) -> "BenchmarkExecution": ...

    @overload
    @staticmethod
    def _from_response_model(
        benchmark_execution_response: BenchmarkExecutionExportMetadata,
        benchmark_uid: int,
    ) -> "BenchmarkExecution": ...

    @staticmethod
    def _from_response_model(
        benchmark_execution_response: (
            BenchmarkExecutionExportMetadata | BenchmarkExecutionApiModel
        ),
        benchmark_uid: Optional[int] = None,
    ) -> "BenchmarkExecution":
        """
        Converts a response dictionary from the API to a BenchmarkExecution object. Intended for internal use only.

        Parameters
        ----------
        benchmark_execution_response
            The response dictionary from the API.
        """
        if isinstance(benchmark_execution_response, BenchmarkExecutionApiModel):
            return BenchmarkExecution(
                benchmark_uid=benchmark_execution_response.benchmark_uid,
                benchmark_execution_uid=benchmark_execution_response.benchmark_execution_uid,
                name=benchmark_execution_response.name,
                created_at=benchmark_execution_response.created_at,
                created_by=benchmark_execution_response.created_by_username,
                archived=benchmark_execution_response.state
                == BenchmarkExecutionState.ARCHIVED,
            )
        else:
            if benchmark_uid is None:
                raise ValueError(
                    "benchmark_uid is required for when using BenchmarkExecutionExportMetadata models"
                )

            return BenchmarkExecution(
                benchmark_uid=benchmark_uid,
                benchmark_execution_uid=benchmark_execution_response.uid,
                name=benchmark_execution_response.name,
                created_at=benchmark_execution_response.created_at,
                created_by=benchmark_execution_response.created_by,
                archived=benchmark_execution_response.state
                == BenchmarkExecutionState.ARCHIVED,
            )

    @staticmethod
    def list(
        benchmark_uid: int, include_archived: bool = False
    ) -> List["BenchmarkExecution"]:
        """
        List all benchmark executions for a given benchmark.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the parent Benchmark. The ``benchmark_uid`` is
            visible in the URL of the benchmark page in the Snorkel GUI. For example,
            ``https://YOUR-SNORKEL-INSTANCE/benchmarks/100/`` indicates a benchmark
            with ``benchmark_uid`` of ``100``.
        include_archived
            Whether to include archived executions. Defaults to False.
        """
        return [
            BenchmarkExecution._from_response_model(
                execution, benchmark_uid=benchmark_uid
            )
            for execution in list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
                benchmark_uid=benchmark_uid,
                include_archived=include_archived,
            )
        ]

    def export(
        self,
        filepath: str,
        config: Optional[BenchmarkExecutionExportConfig] = None,
        connector_config_uid: Optional[int] = None,
    ) -> None:
        """Export information associated with this benchmark execution.
        The exported data includes:

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
            The filepath where you want to write the exported data.
        config
            A ``JsonExportConfig`` or ``CsvExportConfig`` object. Defaults to
            JSON. No additional configuration is required for JSON exports. For
            CSV exports, the following parameters are supported:

            * ``sep``: The separator between columns. Default is ``,``.
            * ``quotechar``: The character used to quote fields. Default is ``"``.
            * ``escapechar``: The character used to escape special characters. Default is ``\\``.
        connector_config_uid
            Optional UID of the connector config to use for the export.
            **Required** only if the export destination is a remote, private
            bucket (a private S3 or GCS bucket that requires credentials).
            **Ignored** if the export destination is a public bucket
            (a public S3 or GCS bucket that does not require credentials) or if
            the export destination is a local file.

        Examples
        --------
        Example 1
        ^^^^^^^^^

        Export a benchmark execution to a local file:

        .. testcode::

            from snorkelai.sdk.develop import Benchmark

            benchmark = Benchmark.get(100)
            execution = benchmark.list_executions()[0]
            execution.export("benchmark_execution.json")

        Example 2
        ^^^^^^^^^

        Export a benchmark execution to a S3 bucket using a connector config:

        .. testcode::

            from snorkelai.sdk.develop import Benchmark

            benchmark = Benchmark.get(100)
            execution = benchmark.list_executions()[0]
            execution.export("s3://MY-BUCKET/MY-PATH/benchmark_execution.json", connector_config_uid=1)
        """
        # Don't use a default value in the function signature so the docs generate more
        # clearly.
        if config is None:
            config = JsonExportConfig()

        if not isinstance(config, (JsonExportConfig, CsvExportConfig)):
            raise ValueError("Invalid export config")

        if config.format == BenchmarkExecutionExportFormat.JSON:
            export_response = export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get(
                benchmark_uid=self.benchmark_uid,
                benchmark_execution_uid=self.uid,
                export_format=config.format,
                connector_config_uid=_wrap_in_unset(connector_config_uid),
                destination_path=filepath,
            )
        else:
            assert isinstance(config, CsvExportConfig)  # mypy
            export_response = export_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__export_get(
                benchmark_uid=self.benchmark_uid,
                benchmark_execution_uid=self.uid,
                export_format=config.format,
                sep=config.sep,
                quotechar=config.quotechar,
                escapechar=config.escapechar,
                raw=True,
                connector_config_uid=_wrap_in_unset(connector_config_uid),
                destination_path=filepath,
            )

        # Write the export response to a file
        download_to_file(export_response, filepath)
        print(f"Benchmark execution exported to {filepath}")

    @classmethod
    def create(
        cls,
        benchmark_uid: int,
        name: Optional[str] = None,
        criteria_uids: Optional[List[int]] = None,
        datasource_uids: Optional[List[int]] = None,
        splits: Optional[List[str]] = None,
    ) -> "BenchmarkExecution":
        """Create a benchmark execution.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark to create an execution for.
        name
            Optional name for the benchmark execution.
        criteria_uids
            List of criteria UIDs to include in the execution.
        datasource_uids
            List of datasource UIDs to include in the execution.
        splits
            List of splits to include in the execution.

        Returns
        -------
        BenchmarkExecution
            The created benchmark execution.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import BenchmarkExecution
            BenchmarkExecution.create(benchmark_uid=123, name="Test Execution",datasource_uids=[1, 2, 3], splits=["train", "test"])
        """
        benchmark = get_benchmark_benchmarks__benchmark_uid__get(benchmark_uid)
        workflow = get_workflow_by_id_workflows__workflow_uid__get(
            benchmark.workflow_uid
        )
        dataset_uid = workflow.input_dataset_uid
        if type(dataset_uid) is not int:
            raise ValueError(
                f"Benchmark {benchmark_uid} does not have an input dataset"
            )

        payload = CreateBenchmarkExecutionPayload(
            name=_wrap_in_unset(name),
            dataset_uid=dataset_uid,
            criteria_uids=_wrap_in_unset(criteria_uids),
            datasource_uids=_wrap_in_unset(datasource_uids),
            splits=_wrap_in_unset(splits),
        )

        api_response = (
            create_benchmark_execution_benchmarks__benchmark_uid__executions_post(
                benchmark_uid=benchmark_uid,
                body=payload,
            )
        )

        return cls._from_response_model(api_response)

    @classmethod
    def get(
        cls, benchmark_uid: int, benchmark_execution_uid: int
    ) -> "BenchmarkExecution":
        """Get a benchmark execution by its unique identifier.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark.
        benchmark_execution_uid
            The unique identifier of the benchmark execution.

        Returns
        -------
        BenchmarkExecution
            The requested benchmark execution.

        Raises
        ------
        ValueError
            If the benchmark execution is not found.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import BenchmarkExecution

            BenchmarkExecution.get(benchmark_uid=123, benchmark_execution_uid=456)
        """
        # Get all executions for this benchmark and find the specific one
        all_executions = list_benchmark_execution_metadata_benchmarks__benchmark_uid__executions_metadata_get(
            benchmark_uid=benchmark_uid,
            include_archived=True,  # Include archived to ensure we can find any execution
        )

        for execution in all_executions:
            if execution.uid == benchmark_execution_uid:
                return cls._from_response_model(execution, benchmark_uid=benchmark_uid)

        raise ValueError(
            f"Benchmark execution with UID {benchmark_execution_uid} not found for benchmark {benchmark_uid}"
        )

    def update(self, archived: bool) -> None:
        """Update the state of the benchmark execution.

        Parameters
        ----------
        archived
            Whether the benchmark execution should be archived.
        """
        update_benchmark_execution_benchmarks__benchmark_uid__execution__benchmark_execution_uid__put(
            benchmark_uid=self.benchmark_uid,
            benchmark_execution_uid=self.uid,
            body=UpdateBenchmarkExecutionPayload(
                state=(
                    BenchmarkExecutionState.ARCHIVED
                    if archived
                    else BenchmarkExecutionState.ACTIVE
                ),
            ),
        )

        self._archived = archived

    @classmethod
    def delete(cls, benchmark_uid: int, benchmark_execution_uid: int) -> None:
        """Delete (archive) a benchmark execution.

        This performs a soft delete by archiving the benchmark execution.
        Hard deletion is not supported.

        Parameters
        ----------
        benchmark_uid
            The unique identifier of the benchmark.
        benchmark_execution_uid
            The unique identifier of the benchmark execution to delete.

        Raises
        ------
        ValueError
            If the benchmark execution is not found.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import BenchmarkExecution
            BenchmarkExecution.delete(benchmark_uid=123, benchmark_execution_uid=456)
        """
        # Get the execution first to ensure it exists
        execution = cls.get(
            benchmark_uid=benchmark_uid, benchmark_execution_uid=benchmark_execution_uid
        )

        # Archive (soft delete) the execution
        execution.update(archived=True)

        print(
            f"Successfully deleted (archived) benchmark execution with UID {benchmark_execution_uid}."
        )
