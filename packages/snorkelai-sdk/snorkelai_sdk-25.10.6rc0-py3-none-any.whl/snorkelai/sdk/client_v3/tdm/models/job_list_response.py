from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.job_info import JobInfo  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="JobListResponse")


@attrs.define
class JobListResponse:
    """
    Attributes:
        jobs (List['JobInfo']):
        next_start_time (float): For pagination purposes. To go forwards one page, set start_time to this value and
            direction to 'older'
        previous_start_time (float): For pagination purposes. To go backwards one page, set start_time to this value and
            direction to 'newer'
    """

    jobs: List["JobInfo"]
    next_start_time: float
    previous_start_time: float
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.job_info import JobInfo  # noqa: F401
        # fmt: on
        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        next_start_time = self.next_start_time
        previous_start_time = self.previous_start_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobs": jobs,
                "next_start_time": next_start_time,
                "previous_start_time": previous_start_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.job_info import JobInfo  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = JobInfo.from_dict(jobs_item_data)

            jobs.append(jobs_item)

        next_start_time = d.pop("next_start_time")

        previous_start_time = d.pop("previous_start_time")

        obj = cls(
            jobs=jobs,
            next_start_time=next_start_time,
            previous_start_time=previous_start_time,
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
