from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="PromptDevStartExecutionResponse")


@attrs.define
class PromptDevStartExecutionResponse:
    """
    Attributes:
        job_id (str):
        prompt_execution_uid (int):
        prompt_uid (int):
    """

    job_id: str
    prompt_execution_uid: int
    prompt_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        job_id = self.job_id
        prompt_execution_uid = self.prompt_execution_uid
        prompt_uid = self.prompt_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "prompt_execution_uid": prompt_execution_uid,
                "prompt_uid": prompt_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_id = d.pop("job_id")

        prompt_execution_uid = d.pop("prompt_execution_uid")

        prompt_uid = d.pop("prompt_uid")

        obj = cls(
            job_id=job_id,
            prompt_execution_uid=prompt_execution_uid,
            prompt_uid=prompt_uid,
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
