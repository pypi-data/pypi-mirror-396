import datetime
from typing import (
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

from ..models.job_state import JobState
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricJobMetadata")


@attrs.define
class MetricJobMetadata:
    """Model for individual metric job metadata tracking.

    This replaces the JSONB array approach to avoid concurrency issues
    when multiple jobs update their metadata simultaneously.

    Attributes:
        metric_job_metadata_uid: Primary key
        benchmark_execution_uid: Foreign key to benchmark execution
        dataset_uid: Dataset identifier
        criteria_uid: Criteria identifier
        score_key: Score key identifier
        splits: List of data splits
        job_uid: Unique job identifier
        job_state: Current state of the job
        error_message: Error message if job failed
        start_time: When the job started
        end_time: When the job ended
        created_at: Record creation timestamp
        updated_at: Record update timestamp

        Attributes:
            benchmark_execution_uid (int):
            criteria_uid (int):
            dataset_uid (int):
            job_state (JobState):
            job_uid (str):
            metric_job_metadata_uid (int):
            score_key (str):
            splits (List[str]):
            created_at (Union[Unset, datetime.datetime]):
            end_time (Union[Unset, datetime.datetime]):
            error_message (Union[Unset, str]):
            start_time (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
    """

    benchmark_execution_uid: int
    criteria_uid: int
    dataset_uid: int
    job_state: JobState
    job_uid: str
    metric_job_metadata_uid: int
    score_key: str
    splits: List[str]
    created_at: Union[Unset, datetime.datetime] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    error_message: Union[Unset, str] = UNSET
    start_time: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        benchmark_execution_uid = self.benchmark_execution_uid
        criteria_uid = self.criteria_uid
        dataset_uid = self.dataset_uid
        job_state = self.job_state.value
        job_uid = self.job_uid
        metric_job_metadata_uid = self.metric_job_metadata_uid
        score_key = self.score_key
        splits = self.splits

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()
        error_message = self.error_message
        start_time: Union[Unset, str] = UNSET
        if not isinstance(self.start_time, Unset):
            start_time = self.start_time.isoformat()
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_execution_uid": benchmark_execution_uid,
                "criteria_uid": criteria_uid,
                "dataset_uid": dataset_uid,
                "job_state": job_state,
                "job_uid": job_uid,
                "metric_job_metadata_uid": metric_job_metadata_uid,
                "score_key": score_key,
                "splits": splits,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if start_time is not UNSET:
            field_dict["start_time"] = start_time
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        benchmark_execution_uid = d.pop("benchmark_execution_uid")

        criteria_uid = d.pop("criteria_uid")

        dataset_uid = d.pop("dataset_uid")

        job_state = JobState(d.pop("job_state"))

        job_uid = d.pop("job_uid")

        metric_job_metadata_uid = d.pop("metric_job_metadata_uid")

        score_key = d.pop("score_key")

        splits = cast(List[str], d.pop("splits"))

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _end_time = d.pop("end_time", UNSET)
        _end_time = UNSET if _end_time is None else _end_time
        end_time: Union[Unset, datetime.datetime]
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        _error_message = d.pop("error_message", UNSET)
        error_message = UNSET if _error_message is None else _error_message

        _start_time = d.pop("start_time", UNSET)
        _start_time = UNSET if _start_time is None else _start_time
        start_time: Union[Unset, datetime.datetime]
        if isinstance(_start_time, Unset):
            start_time = UNSET
        else:
            start_time = isoparse(_start_time)

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            benchmark_execution_uid=benchmark_execution_uid,
            criteria_uid=criteria_uid,
            dataset_uid=dataset_uid,
            job_state=job_state,
            job_uid=job_uid,
            metric_job_metadata_uid=metric_job_metadata_uid,
            score_key=score_key,
            splits=splits,
            created_at=created_at,
            end_time=end_time,
            error_message=error_message,
            start_time=start_time,
            updated_at=updated_at,
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
