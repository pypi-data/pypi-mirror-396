import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ErrorAnalysisRun")


@attrs.define
class ErrorAnalysisRun:
    """Model for error analysis runs that cluster LLM disagreements with ground truth.

    Attributes:
        created_at (datetime.datetime):
        error_analysis_uid (int):
        prompt_execution_uid (int):
        updated_at (datetime.datetime):
        job_uid (Union[Unset, str]):
    """

    created_at: datetime.datetime
    error_analysis_uid: int
    prompt_execution_uid: int
    updated_at: datetime.datetime
    job_uid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()
        error_analysis_uid = self.error_analysis_uid
        prompt_execution_uid = self.prompt_execution_uid
        updated_at = self.updated_at.isoformat()
        job_uid = self.job_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "error_analysis_uid": error_analysis_uid,
                "prompt_execution_uid": prompt_execution_uid,
                "updated_at": updated_at,
            }
        )
        if job_uid is not UNSET:
            field_dict["job_uid"] = job_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        error_analysis_uid = d.pop("error_analysis_uid")

        prompt_execution_uid = d.pop("prompt_execution_uid")

        updated_at = isoparse(d.pop("updated_at"))

        _job_uid = d.pop("job_uid", UNSET)
        job_uid = UNSET if _job_uid is None else _job_uid

        obj = cls(
            created_at=created_at,
            error_analysis_uid=error_analysis_uid,
            prompt_execution_uid=prompt_execution_uid,
            updated_at=updated_at,
            job_uid=job_uid,
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
