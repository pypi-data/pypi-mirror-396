from datetime import datetime
from typing import List, Optional, final

import pandas as pd
from requests import HTTPError

from snorkelai.sdk.client_v3.tdm.api.cluster import (
    get_cluster_cluster__cluster_uid__get as get_cluster_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.cluster import (
    update_cluster_clusters__cluster_uid__put as update_cluster_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.error_analysis import (
    get_error_analysis_clusters_benchmarks__benchmark_uid__error_analysis__error_analysis_run_id__clusters_get as get_error_analysis_clusters_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.virtualized_dataset import (
    get_paginated_data_virtualized_dataset__virtualized_dataset_uid__data_get as get_vds_data_autogen,
)
from snorkelai.sdk.client_v3.tdm.models.cluster import Cluster as BECluster
from snorkelai.sdk.client_v3.tdm.models.update_cluster_request import (
    UpdateClusterRequest,
)
from snorkelai.sdk.client_v3.tdm.types import Unset
from snorkelai.sdk.client_v3.utils import _wrap_in_unset
from snorkelai.sdk.develop.base import Base


@final
class Cluster(Base):
    """
    Provides methods for viewing and updating clusters and the ability to view datapoints assigned to a cluster.

    Clusters represent groups of similar datapoints identified during error analysis. They help identify
    common failure patterns in model predictions and provide insights for targeted improvements.
    Clusters can currently only be created and deleted through the ErrorAnalysis class.

    Read more in the `Error Analysis Guide <https://docs.snorkel.ai/docs/user-guide/evaluation/improve-llmaj-alignment#error-analysis>`_.

    Using the ``Cluster`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import Cluster
    """

    @staticmethod
    def _get_sdk_cluster_from_be_cluster(cluster: BECluster) -> "Cluster":
        return Cluster(
            cluster_uid=cluster.cluster_uid,
            error_analysis_uid=cluster.error_analysis_uid,
            name=cluster.name,
            description=(
                cluster.description
                if not isinstance(cluster.description, Unset)
                else None
            ),
            improvement_strategy=(
                cluster.improvement_strategy
                if not isinstance(cluster.improvement_strategy, Unset)
                else None
            ),
            examples=(
                cluster.examples if not isinstance(cluster.examples, Unset) else None
            ),
            datapoint_count=(
                cluster.datapoint_count
                if not isinstance(cluster.datapoint_count, Unset)
                else 0
            ),
            virtualized_dataset_uid=(
                cluster.virtualized_dataset_uid
                if not isinstance(cluster.virtualized_dataset_uid, Unset)
                else None
            ),
            created_at=(
                cluster.created_at
                if not isinstance(cluster.created_at, Unset)
                else None
            ),
            updated_at=(
                cluster.updated_at
                if not isinstance(cluster.updated_at, Unset)
                else None
            ),
        )

    def __init__(
        self,
        cluster_uid: int,
        error_analysis_uid: int,
        name: str,
        description: Optional[str] = None,
        improvement_strategy: Optional[str] = None,
        examples: Optional[List[str]] = None,
        datapoint_count: int = 0,
        virtualized_dataset_uid: Optional[int] = None,
        created_at: Optional[datetime] = datetime.now(),
        updated_at: Optional[datetime] = datetime.now(),
    ):
        """Initializes a Cluster instance.

        Parameters
        ----------
        cluster_uid
            Unique identifier for the cluster.
        error_analysis_uid
            Unique identifier for the associated error analysis run.
        name
            Name of the cluster.
        description
            Description of the cluster.
        improvement_strategy
            Suggested improvement strategy for the cluster.
        examples
            Example datapoints in the cluster.
        datapoint_count
            Number of datapoints in the cluster.
        virtualized_dataset_uid
            Unique identifier for the virtualized dataset containing the datapoints in the cluster.
        created_at
            Timestamp when the cluster was created.
        updated_at
            Timestamp when the cluster was last updated.
        """
        self._cluster_uid = cluster_uid
        self._error_analysis_uid = error_analysis_uid
        self._name = name
        self._description = description
        self._improvement_strategy = improvement_strategy
        self._examples = examples
        self._datapoint_count = datapoint_count
        self._virtualized_dataset_uid = virtualized_dataset_uid
        self._created_at = created_at if created_at else datetime.now()
        self._updated_at = updated_at if updated_at else datetime.now()

    @property
    def uid(self) -> int:
        """The unique identifier for the cluster."""
        return self._cluster_uid

    @property
    def error_analysis_uid(self) -> int:
        """The unique identifier for the associated error analysis run."""
        return self._error_analysis_uid

    @property
    def name(self) -> str:
        """The name of the cluster."""
        return self._name

    @property
    def description(self) -> Optional[str]:
        """The description of the cluster."""
        return self._description

    @property
    def improvement_strategy(self) -> Optional[str]:
        """The suggested improvement strategy for the cluster."""
        return self._improvement_strategy

    @property
    def examples(self) -> Optional[List[str]]:
        """Example datapoints in the cluster."""
        return self._examples

    @property
    def datapoint_count(self) -> int:
        """The number of datapoints in the cluster."""
        return self._datapoint_count

    @property
    def virtualized_dataset_uid(self) -> Optional[int]:
        """The unique identifier for the virtualized dataset containing the datapoints in the cluster."""
        return self._virtualized_dataset_uid

    @property
    def created_at(self) -> datetime:
        """The timestamp when the cluster was created."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """The timestamp when the cluster was last updated."""
        return self._updated_at

    @classmethod
    def get(cls, cluster_uid: int) -> "Cluster":
        """Retrieves an existing cluster by its unique identifier.

        Parameters
        ----------
        cluster_uid
            Unique identifier of the cluster to retrieve.

        Returns
        -------
        Cluster
            The Cluster instance for the specified cluster.

        Raises
        ------
        ValueError
            If no cluster exists with the given ID.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Cluster
            cluster = Cluster.get(cluster_uid=123)
        """
        cluster = get_cluster_autogen(cluster_uid)
        if cluster is None:
            raise ValueError(f"No cluster found with uid {cluster_uid}")

        return cls._get_sdk_cluster_from_be_cluster(cluster)

    @classmethod
    def create(cls) -> "Cluster":
        """Creates this cluster.

        Raises
        ------
        NotImplementedError
            Cluster creation is not supported directly. Use ErrorAnalysis to create clusters.
        """
        raise NotImplementedError(
            "Creating clusters directly is not supported. Please create clusters through the ErrorAnalysis class."
        )

    @classmethod
    def delete(cls, cluster_uid: int) -> None:
        """Deletes this cluster.

        Parameters
        ----------
        cluster_uid
            Unique identifier of the cluster to delete.

        Raises
        ------
        NotImplementedError
            Cluster deletion is not supported. Delete the associated error analysis run to remove clusters.
        """
        raise NotImplementedError(
            "Cluster deletion is not supported. Delete the associated error analysis run to remove clusters."
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Updates the cluster properties.

        Parameters
        ----------
        name
            The new name for the cluster, by default None.
        description
            The new description for the cluster, by default None.

        Raises
        ------
        ValueError
            If there are other errors during cluster update.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Cluster
            cluster = Cluster.get(cluster_uid=123)
            cluster.update(name="New cluster name", description="Updated description")
        """
        cluster_update_request = UpdateClusterRequest(
            name=_wrap_in_unset(name),
            description=_wrap_in_unset(description),
        )
        try:
            update_cluster_autogen(cluster_uid=self.uid, body=cluster_update_request)
            self._name = name or self._name
            self._description = description or self._description

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
        except Exception as e:
            raise ValueError("Failed to update cluster") from e

    @classmethod
    def get_clusters(
        cls, error_analysis_uid: int, benchmark_uid: int
    ) -> List["Cluster"]:
        """Fetches clusters from a completed error analysis.

        Parameters
        ----------
        error_analysis_uid
            Unique identifier of the error analysis run.
        benchmark_uid
            Unique identifier of the benchmark associated with the error analysis run.

        Returns
        -------
        List[Cluster]
            List of clusters.

        Raises
        ------
        RuntimeError
            If called before analysis is complete.
        ValueError
            If analysis failed or was deleted.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Cluster
            clusters = Cluster.get_clusters(error_analysis_uid=123, benchmark_uid=456)
        """
        try:
            clusters_response = get_error_analysis_clusters_autogen(
                benchmark_uid=benchmark_uid,
                error_analysis_run_id=error_analysis_uid,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
        except Exception as e:
            raise ValueError("Failed to get clusters") from e

        clusters: list[Cluster] = [
            cls._get_sdk_cluster_from_be_cluster(cluster)
            for cluster in clusters_response
        ]

        return clusters

    def get_cluster_membership(self) -> pd.DataFrame:
        """Fetches datapoint membership for a specific cluster.

        Returns
        -------
        pd.DataFrame
            DataFrame containing all the datapoints in the cluster.

        Raises
        ------
        ValueError
            If there are no datapoints assigned to the cluster.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Cluster
            cluster = Cluster.get(cluster_uid=123)
            membership_df = cluster.get_cluster_membership()
        """
        limit = self.datapoint_count
        if (
            limit == 0
            or self.virtualized_dataset_uid is None
            or isinstance(self.virtualized_dataset_uid, Unset)
        ):
            raise ValueError(f"No datapoints assigned to cluster {self.uid}")
        data_dict = get_vds_data_autogen(
            virtualized_dataset_uid=self.virtualized_dataset_uid,
            limit=limit,
        )["data"]
        return pd.DataFrame(data=data_dict)
