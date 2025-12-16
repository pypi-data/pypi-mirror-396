from typing import Dict, List, Optional, final

from requests import HTTPError
from typing_extensions import Self

from snorkelai.sdk.client_v3.tdm.api.benchmark import (
    get_benchmarks_by_workflow_uid_or_workspace_uid_benchmarks_get as get_benchmarks_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.criteria import (
    get_benchmark_uid_from_criteria_uid_criteria__criteria_uid__benchmark_uid_get as get_benchmark_uid_from_criteria_uid_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    create_error_analysis_run_benchmarks__benchmark_uid__error_analysis_post as create_error_analysis_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    delete_error_analysis_run_error_analysis__error_analysis_run_id__delete as delete_error_analysis_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    get_error_analysis_clusters_benchmarks__benchmark_uid__error_analysis__error_analysis_run_id__clusters_get as get_error_analysis_clusters_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    get_error_analysis_run_error_analysis__error_analysis_run_id__get as get_error_analysis_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    get_latest_error_analysis_run_benchmarks__benchmark_uid__error_analysis_latest_run_get as get_latest_error_analysis_run_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.prompt_execution import (
    get_criteria_uid_prompt_execution__prompt_execution_uid__criteria_get as get_criteria_uid_autogen,
)
from snorkelai.sdk.client_v3.tdm.models.create_error_analysis_request import (
    CreateErrorAnalysisRequest,
)
from snorkelai.sdk.client_v3.tdm.types import Unset
from snorkelai.sdk.client_v3.utils import poll_job_status
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.develop.cluster import Cluster


@final
class ErrorAnalysis(Base):
    """
    Provides methods for creating, monitoring, and retrieving results from error analysis clustering runs.

    The clustering algorithm identifies patterns in LLM evaluation failures and groups similar errors together.
    This enables systematic analysis of model performance issues and identification of common failure modes.

    Read more in the `Error Analysis Guide <https://docs.snorkel.ai/docs/user-guide/evaluation/improve-llmaj-alignment#error-analysis>`_.

    Using the ``ErrorAnalysis`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import ErrorAnalysis
    """

    @staticmethod
    def _get_benchmark_uid_from_workflow(workflow_uid: int) -> int:
        """Internal method to get benchmark_uid from workflow_uid.

        Parameters
        ----------
        workflow_uid : int
            The workflow UID.

        Returns
        -------
        int
            The benchmark UID.

        Raises
        ------
        ValueError
            If no benchmark can be found for the workflow.
        """
        try:
            benchmarks = get_benchmarks_autogen(workflow_uid=workflow_uid)

            if not benchmarks:
                raise ValueError(f"No benchmark found for workflow {workflow_uid}")

            if len(benchmarks) > 1:
                raise ValueError(
                    f"Multiple benchmarks found for workflow {workflow_uid}"
                )

            return benchmarks[0].benchmark_uid

        except Exception as e:
            raise ValueError(f"No benchmark found for workflow {workflow_uid}") from e

    def __init__(self, provenance: Dict[str, int], error_analysis_run_uid: int):
        """Initializes an ErrorAnalysis instance.

        Parameters
        ----------
        provenance
            Tracking information that uniquely identifies the inputs used to create this cluster analysis.
        error_analysis_run_uid
            Unique identifier for this specific cluster analysis run.
        """
        self.provenance = provenance
        self.error_analysis_run_uid = error_analysis_run_uid

    @property
    def uid(self) -> int:
        """Return the UID of the error analysis run"""
        return self.error_analysis_run_uid

    @classmethod
    def create(
        cls, prompt_execution_uid: int, *, sync: bool = False
    ) -> "ErrorAnalysis":
        """Creates and triggers error analysis clustering job for LLM evaluation results.

        Parameters
        ----------
        prompt_execution_uid
            Unique identifier of the prompt execution.
        sync
            If ``True``, method blocks until clustering completes and returns ready ErrorAnalysis.
            If ``False``, returns immediately with ErrorAnalysis that requires waiting to get clusters.

        Returns
        -------
        ErrorAnalysis
            An ErrorAnalysis instance representing the clustering job. If sync = ``False``,
            get_clusters will fail until analysis is complete. If sync = ``True``, results
            are immediately available.

        Raises
        ------
        ValueError
            If benchmark, prompt execution or criteria don't exist or are not valid.
        ValueError
            If prompt execution has no evaluation results or insufficient error cases to cluster.

        Examples
        --------
        Example 1
        ^^^^^^^^^

        Create error analysis asynchronously:

        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            error_analysis = ErrorAnalysis.create(
                prompt_execution_uid=456,
                sync=False
            )

        Example 2
        ^^^^^^^^^

        Create error analysis synchronously:

        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            error_analysis = ErrorAnalysis.create(
                prompt_execution_uid=456,
                sync=True
            )
        """
        criteria_uid = get_criteria_uid_autogen(prompt_execution_uid)
        benchmark_uid = get_benchmark_uid_from_criteria_uid_autogen(criteria_uid)

        try:
            request = CreateErrorAnalysisRequest(
                criteria_uid=criteria_uid, prompt_execution_uid=prompt_execution_uid
            )
            response = create_error_analysis_autogen(
                benchmark_uid=benchmark_uid, body=request
            )
            provenance: Dict[str, int] = {
                "benchmark_uid": benchmark_uid,
                "criteria_uid": criteria_uid,
                "prompt_execution_uid": prompt_execution_uid,
            }
            error_analysis = cls(
                provenance=provenance,
                error_analysis_run_uid=response.error_analysis_run_id,
            )

            if sync:
                error_analysis_obj = get_error_analysis_autogen(
                    error_analysis.error_analysis_run_uid
                )
                job_uid = error_analysis_obj.job_uid
                if job_uid is not None and not isinstance(job_uid, Unset):
                    poll_job_status(job_uid)

            return error_analysis

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
        except Exception as e:
            raise ValueError("Failed to create error analysis") from e

    @classmethod
    def get(cls, error_analysis_run_uid: int) -> Self:
        """Retrieves an existing error analysis by its unique run identifier.

        Parameters
        ----------
        error_analysis_run_uid
            The unique identifier of the error analysis run to retrieve.

        Returns
        -------
        ErrorAnalysis
            The ErrorAnalysis instance for the specified run, ready for status checks and results retrieval.

        Raises
        ------
        ValueError
            If no error analysis run exists with the given ID.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            error_analysis = ErrorAnalysis.get(error_analysis_run_uid=42)
        """
        error_analysis_run = get_error_analysis_autogen(error_analysis_run_uid)
        prompt_execution_uid = error_analysis_run.prompt_execution_uid
        criteria_uid = get_criteria_uid_autogen(prompt_execution_uid)
        benchmark_uid = get_benchmark_uid_from_criteria_uid_autogen(criteria_uid)

        return cls(
            provenance={
                "prompt_execution_uid": prompt_execution_uid,
                "benchmark_uid": benchmark_uid,
                "criteria_uid": criteria_uid,
            },
            error_analysis_run_uid=error_analysis_run_uid,
        )

    def update(self) -> None:
        """Update an error analysis run"""
        raise NotImplementedError("Not implemented")

    @classmethod
    def delete(cls, error_analysis_run_uid: int) -> None:
        """Deletes this error analysis run and all associated cluster data.

        Parameters
        ----------
        error_analysis_run_uid
            The unique identifier of the error analysis run to delete.

        Raises
        ------
        ValueError
            If the error analysis run has already been deleted or does not exist.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            ErrorAnalysis.delete(error_analysis_run_uid=42)
        """
        delete_error_analysis_autogen(error_analysis_run_uid)

    @classmethod
    def get_latest(cls, prompt_execution_uid: int) -> Optional["ErrorAnalysis"]:
        """Gets the most recent error analysis run for a specific prompt execution.

        Parameters
        ----------
        prompt_execution_uid
            The unique identifier of the prompt execution.

        Returns
        -------
        ErrorAnalysis or None
            The most recent ErrorAnalysis for the prompt execution or None if no error analysis
            has been run for this prompt execution.

        Raises
        ------
        ValueError
            If prompt execution does not exist.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            latest_analysis = ErrorAnalysis.get_latest(
                prompt_execution_uid=456
            )
        """
        try:
            criteria_uid = get_criteria_uid_autogen(prompt_execution_uid)
            benchmark_uid = get_benchmark_uid_from_criteria_uid_autogen(criteria_uid)

            response = get_latest_error_analysis_run_autogen(
                benchmark_uid=benchmark_uid, prompt_execution_uid=prompt_execution_uid
            )

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
        except Exception as e:
            raise ValueError("Failed to get latest error analysis") from e

        if (
            response is None
            or isinstance(response.error_analysis_run_id, Unset)
            or response.error_analysis_run_id is None
        ):
            raise ValueError(
                f"No error analysis run found for prompt execution {prompt_execution_uid}"
            )

        provenance: Dict[str, int] = {
            "benchmark_uid": benchmark_uid,
            "criteria_uid": criteria_uid,
            "prompt_execution_uid": prompt_execution_uid,
        }

        return cls(
            provenance=provenance,
            error_analysis_run_uid=response.error_analysis_run_id,
        )

    def get_clusters(self) -> List[Cluster]:
        """Fetches clusters from a completed error analysis.

        Returns
        -------
        List[Cluster]
            List of cluster objects.

        Raises
        ------
        RuntimeError
            If called before analysis is complete.
        ValueError
            If analysis failed or was deleted.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import ErrorAnalysis
            analysis = ErrorAnalysis.get(error_analysis_run_uid=42)
            clusters = analysis.get_clusters()
        """
        try:
            benchmark_uid = self.provenance["benchmark_uid"]

            clusters_response = get_error_analysis_clusters_autogen(
                benchmark_uid=benchmark_uid,
                error_analysis_run_id=self.error_analysis_run_uid,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
        except Exception as e:
            raise ValueError("Failed to get clusters") from e

        # Convert Cluster objects to dictionaries as specified in the interface
        clusters = []
        for cluster in clusters_response:
            cluster_obj: Cluster = Cluster._get_sdk_cluster_from_be_cluster(cluster)
            clusters.append(cluster_obj)

        return clusters
