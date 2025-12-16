import datetime
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
from dateutil.parser import isoparse

from ..models.job_state import JobState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PromptExecution")


@attrs.define
class PromptExecution:
    """
    Attributes:
        created_at (datetime.datetime):
        prompt_execution_uid (int):
        prompt_uid (int):
        user_uid (int):
        job_detail (Union[Unset, str]):
        job_id (Union[Unset, str]):
        status (Union[Unset, JobState]):
        virtualized_dataset_metadata (Union[Unset, ExecutionVDSMetadata]):
        virtualized_dataset_uid (Union[Unset, int]):
    """

    created_at: datetime.datetime
    prompt_execution_uid: int
    prompt_uid: int
    user_uid: int
    job_detail: Union[Unset, str] = UNSET
    job_id: Union[Unset, str] = UNSET
    status: Union[Unset, JobState] = UNSET
    virtualized_dataset_metadata: Union[Unset, "ExecutionVDSMetadata"] = UNSET
    virtualized_dataset_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        created_at = self.created_at.isoformat()
        prompt_execution_uid = self.prompt_execution_uid
        prompt_uid = self.prompt_uid
        user_uid = self.user_uid
        job_detail = self.job_detail
        job_id = self.job_id
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        virtualized_dataset_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.virtualized_dataset_metadata, Unset):
            virtualized_dataset_metadata = self.virtualized_dataset_metadata.to_dict()
        virtualized_dataset_uid = self.virtualized_dataset_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "prompt_execution_uid": prompt_execution_uid,
                "prompt_uid": prompt_uid,
                "user_uid": user_uid,
            }
        )
        if job_detail is not UNSET:
            field_dict["job_detail"] = job_detail
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if status is not UNSET:
            field_dict["status"] = status
        if virtualized_dataset_metadata is not UNSET:
            field_dict["virtualized_dataset_metadata"] = virtualized_dataset_metadata
        if virtualized_dataset_uid is not UNSET:
            field_dict["virtualized_dataset_uid"] = virtualized_dataset_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        prompt_execution_uid = d.pop("prompt_execution_uid")

        prompt_uid = d.pop("prompt_uid")

        user_uid = d.pop("user_uid")

        _job_detail = d.pop("job_detail", UNSET)
        job_detail = UNSET if _job_detail is None else _job_detail

        _job_id = d.pop("job_id", UNSET)
        job_id = UNSET if _job_id is None else _job_id

        _status = d.pop("status", UNSET)
        _status = UNSET if _status is None else _status
        status: Union[Unset, JobState]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = JobState(_status)

        _virtualized_dataset_metadata = d.pop("virtualized_dataset_metadata", UNSET)
        _virtualized_dataset_metadata = (
            UNSET
            if _virtualized_dataset_metadata is None
            else _virtualized_dataset_metadata
        )
        virtualized_dataset_metadata: Union[Unset, ExecutionVDSMetadata]
        if isinstance(_virtualized_dataset_metadata, Unset):
            virtualized_dataset_metadata = UNSET
        else:
            virtualized_dataset_metadata = ExecutionVDSMetadata.from_dict(
                _virtualized_dataset_metadata
            )

        _virtualized_dataset_uid = d.pop("virtualized_dataset_uid", UNSET)
        virtualized_dataset_uid = (
            UNSET if _virtualized_dataset_uid is None else _virtualized_dataset_uid
        )

        obj = cls(
            created_at=created_at,
            prompt_execution_uid=prompt_execution_uid,
            prompt_uid=prompt_uid,
            user_uid=user_uid,
            job_detail=job_detail,
            job_id=job_id,
            status=status,
            virtualized_dataset_metadata=virtualized_dataset_metadata,
            virtualized_dataset_uid=virtualized_dataset_uid,
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
