from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.rq_job_id import RQJobId  # noqa: F401
    from ..models.rq_meta_job_id import RQMetaJobId  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="JobGroup")


@attrs.define
class JobGroup:
    """
    Attributes:
        jobs (List['RQJobId']):
        meta_job_id (Union[Unset, RQMetaJobId]):
    """

    jobs: List["RQJobId"]
    meta_job_id: Union[Unset, "RQMetaJobId"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.rq_job_id import RQJobId  # noqa: F401
        from ..models.rq_meta_job_id import RQMetaJobId  # noqa: F401
        # fmt: on
        jobs = []
        for jobs_item_data in self.jobs:
            jobs_item = jobs_item_data.to_dict()
            jobs.append(jobs_item)

        meta_job_id: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.meta_job_id, Unset):
            meta_job_id = self.meta_job_id.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "jobs": jobs,
            }
        )
        if meta_job_id is not UNSET:
            field_dict["meta_job_id"] = meta_job_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.rq_job_id import RQJobId  # noqa: F401
        from ..models.rq_meta_job_id import RQMetaJobId  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        jobs = []
        _jobs = d.pop("jobs")
        for jobs_item_data in _jobs:
            jobs_item = RQJobId.from_dict(jobs_item_data)

            jobs.append(jobs_item)

        _meta_job_id = d.pop("meta_job_id", UNSET)
        _meta_job_id = UNSET if _meta_job_id is None else _meta_job_id
        meta_job_id: Union[Unset, RQMetaJobId]
        if isinstance(_meta_job_id, Unset):
            meta_job_id = UNSET
        else:
            meta_job_id = RQMetaJobId.from_dict(_meta_job_id)

        obj = cls(
            jobs=jobs,
            meta_job_id=meta_job_id,
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
