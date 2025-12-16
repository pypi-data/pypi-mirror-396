import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs
from dateutil.parser import isoparse

from ..models.benchmark_execution_state import BenchmarkExecutionState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.benchmark_snapshot import BenchmarkSnapshot  # noqa: F401
    from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="BenchmarkExecution")


@attrs.define
class BenchmarkExecution:
    """
    Attributes:
        benchmark_execution_uid (int):
        benchmark_snapshot (BenchmarkSnapshot):
        benchmark_uid (int):
        created_at (datetime.datetime):
        created_by_username (str):
        dataset_uid (int):
        datasource_uids (List[int]):
        name (str):
        splits (List[str]):
        user_uid (int):
        description (Union[Unset, str]):
        metric_gather_job_uid (Union[Unset, str]):
        metric_job_metadata (Union[Unset, List['MetricJobMetadata']]):
        state (Union[Unset, BenchmarkExecutionState]):
    """

    benchmark_execution_uid: int
    benchmark_snapshot: "BenchmarkSnapshot"
    benchmark_uid: int
    created_at: datetime.datetime
    created_by_username: str
    dataset_uid: int
    datasource_uids: List[int]
    name: str
    splits: List[str]
    user_uid: int
    description: Union[Unset, str] = UNSET
    metric_gather_job_uid: Union[Unset, str] = UNSET
    metric_job_metadata: Union[Unset, List["MetricJobMetadata"]] = UNSET
    state: Union[Unset, BenchmarkExecutionState] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.benchmark_snapshot import BenchmarkSnapshot  # noqa: F401
        from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
        # fmt: on
        benchmark_execution_uid = self.benchmark_execution_uid
        benchmark_snapshot = self.benchmark_snapshot.to_dict()
        benchmark_uid = self.benchmark_uid
        created_at = self.created_at.isoformat()
        created_by_username = self.created_by_username
        dataset_uid = self.dataset_uid
        datasource_uids = self.datasource_uids

        name = self.name
        splits = self.splits

        user_uid = self.user_uid
        description = self.description
        metric_gather_job_uid = self.metric_gather_job_uid
        metric_job_metadata: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metric_job_metadata, Unset):
            metric_job_metadata = []
            for metric_job_metadata_item_data in self.metric_job_metadata:
                metric_job_metadata_item = metric_job_metadata_item_data.to_dict()
                metric_job_metadata.append(metric_job_metadata_item)

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_execution_uid": benchmark_execution_uid,
                "benchmark_snapshot": benchmark_snapshot,
                "benchmark_uid": benchmark_uid,
                "created_at": created_at,
                "created_by_username": created_by_username,
                "dataset_uid": dataset_uid,
                "datasource_uids": datasource_uids,
                "name": name,
                "splits": splits,
                "user_uid": user_uid,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if metric_gather_job_uid is not UNSET:
            field_dict["metric_gather_job_uid"] = metric_gather_job_uid
        if metric_job_metadata is not UNSET:
            field_dict["metric_job_metadata"] = metric_job_metadata
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.benchmark_snapshot import BenchmarkSnapshot  # noqa: F401
        from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark_execution_uid = d.pop("benchmark_execution_uid")

        benchmark_snapshot = BenchmarkSnapshot.from_dict(d.pop("benchmark_snapshot"))

        benchmark_uid = d.pop("benchmark_uid")

        created_at = isoparse(d.pop("created_at"))

        created_by_username = d.pop("created_by_username")

        dataset_uid = d.pop("dataset_uid")

        datasource_uids = cast(List[int], d.pop("datasource_uids"))

        name = d.pop("name")

        splits = cast(List[str], d.pop("splits"))

        user_uid = d.pop("user_uid")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _metric_gather_job_uid = d.pop("metric_gather_job_uid", UNSET)
        metric_gather_job_uid = (
            UNSET if _metric_gather_job_uid is None else _metric_gather_job_uid
        )

        _metric_job_metadata = d.pop("metric_job_metadata", UNSET)
        metric_job_metadata = []
        _metric_job_metadata = (
            UNSET if _metric_job_metadata is None else _metric_job_metadata
        )
        for metric_job_metadata_item_data in _metric_job_metadata or []:
            metric_job_metadata_item = MetricJobMetadata.from_dict(
                metric_job_metadata_item_data
            )

            metric_job_metadata.append(metric_job_metadata_item)

        _state = d.pop("state", UNSET)
        _state = UNSET if _state is None else _state
        state: Union[Unset, BenchmarkExecutionState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = BenchmarkExecutionState(_state)

        obj = cls(
            benchmark_execution_uid=benchmark_execution_uid,
            benchmark_snapshot=benchmark_snapshot,
            benchmark_uid=benchmark_uid,
            created_at=created_at,
            created_by_username=created_by_username,
            dataset_uid=dataset_uid,
            datasource_uids=datasource_uids,
            name=name,
            splits=splits,
            user_uid=user_uid,
            description=description,
            metric_gather_job_uid=metric_gather_job_uid,
            metric_job_metadata=metric_job_metadata,
            state=state,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
