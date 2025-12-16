from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.job_state import JobState
from ..types import UNSET, Unset

T = TypeVar("T", bound="PromptDevExecutionJobStatus")


@attrs.define
class PromptDevExecutionJobStatus:
    """
    Attributes:
        job_id (str):
        job_status (JobState):
        prompt_execution_uid (int):
        job_error_message (Union[Unset, str]):  Default: ''.
        job_error_type (Union[Unset, str]):  Default: ''.
        job_percentage (Union[Unset, int]):  Default: 100.
    """

    job_id: str
    job_status: JobState
    prompt_execution_uid: int
    job_error_message: Union[Unset, str] = ""
    job_error_type: Union[Unset, str] = ""
    job_percentage: Union[Unset, int] = 100
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        job_id = self.job_id
        job_status = self.job_status.value
        prompt_execution_uid = self.prompt_execution_uid
        job_error_message = self.job_error_message
        job_error_type = self.job_error_type
        job_percentage = self.job_percentage

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "job_status": job_status,
                "prompt_execution_uid": prompt_execution_uid,
            }
        )
        if job_error_message is not UNSET:
            field_dict["job_error_message"] = job_error_message
        if job_error_type is not UNSET:
            field_dict["job_error_type"] = job_error_type
        if job_percentage is not UNSET:
            field_dict["job_percentage"] = job_percentage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_id = d.pop("job_id")

        job_status = JobState(d.pop("job_status"))

        prompt_execution_uid = d.pop("prompt_execution_uid")

        _job_error_message = d.pop("job_error_message", UNSET)
        job_error_message = UNSET if _job_error_message is None else _job_error_message

        _job_error_type = d.pop("job_error_type", UNSET)
        job_error_type = UNSET if _job_error_type is None else _job_error_type

        _job_percentage = d.pop("job_percentage", UNSET)
        job_percentage = UNSET if _job_percentage is None else _job_percentage

        obj = cls(
            job_id=job_id,
            job_status=job_status,
            prompt_execution_uid=prompt_execution_uid,
            job_error_message=job_error_message,
            job_error_type=job_error_type,
            job_percentage=job_percentage,
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
