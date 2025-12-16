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
from ..models.job_state import JobState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ExecutionsResponseBenchmarkExecution")


@attrs.define
class ExecutionsResponseBenchmarkExecution:
    """
    Attributes:
        benchmark_execution_uid (int):
        benchmark_uid (int):
        dataset_uid (int):
        name (str):
        splits (List[str]):
        stale (bool):
        created_at (Union[Unset, datetime.datetime]):
        created_by_username (Union[Unset, str]):
        description (Union[Unset, str]):
        metric_gather_job_state (Union[Unset, JobState]):
        metric_gather_job_uid (Union[Unset, str]):
        metric_job_metadata (Union[Unset, List['MetricJobMetadata']]):
        state (Union[Unset, BenchmarkExecutionState]):
    """

    benchmark_execution_uid: int
    benchmark_uid: int
    dataset_uid: int
    name: str
    splits: List[str]
    stale: bool
    created_at: Union[Unset, datetime.datetime] = UNSET
    created_by_username: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    metric_gather_job_state: Union[Unset, JobState] = UNSET
    metric_gather_job_uid: Union[Unset, str] = UNSET
    metric_job_metadata: Union[Unset, List["MetricJobMetadata"]] = UNSET
    state: Union[Unset, BenchmarkExecutionState] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
        # fmt: on
        benchmark_execution_uid = self.benchmark_execution_uid
        benchmark_uid = self.benchmark_uid
        dataset_uid = self.dataset_uid
        name = self.name
        splits = self.splits

        stale = self.stale
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        created_by_username = self.created_by_username
        description = self.description
        metric_gather_job_state: Union[Unset, str] = UNSET
        if not isinstance(self.metric_gather_job_state, Unset):
            metric_gather_job_state = self.metric_gather_job_state.value

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
                "benchmark_uid": benchmark_uid,
                "dataset_uid": dataset_uid,
                "name": name,
                "splits": splits,
                "stale": stale,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by_username is not UNSET:
            field_dict["created_by_username"] = created_by_username
        if description is not UNSET:
            field_dict["description"] = description
        if metric_gather_job_state is not UNSET:
            field_dict["metric_gather_job_state"] = metric_gather_job_state
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
        from ..models.metric_job_metadata import MetricJobMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark_execution_uid = d.pop("benchmark_execution_uid")

        benchmark_uid = d.pop("benchmark_uid")

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        splits = cast(List[str], d.pop("splits"))

        stale = d.pop("stale")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _created_by_username = d.pop("created_by_username", UNSET)
        created_by_username = (
            UNSET if _created_by_username is None else _created_by_username
        )

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _metric_gather_job_state = d.pop("metric_gather_job_state", UNSET)
        _metric_gather_job_state = (
            UNSET if _metric_gather_job_state is None else _metric_gather_job_state
        )
        metric_gather_job_state: Union[Unset, JobState]
        if isinstance(_metric_gather_job_state, Unset):
            metric_gather_job_state = UNSET
        else:
            metric_gather_job_state = JobState(_metric_gather_job_state)

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
            benchmark_uid=benchmark_uid,
            dataset_uid=dataset_uid,
            name=name,
            splits=splits,
            stale=stale,
            created_at=created_at,
            created_by_username=created_by_username,
            description=description,
            metric_gather_job_state=metric_gather_job_state,
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
