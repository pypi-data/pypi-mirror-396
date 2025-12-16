from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateErrorAnalysisRequest")


@attrs.define
class CreateErrorAnalysisRequest:
    """Request payload for creating an error analysis run.

    Attributes:
        criteria_uid (int):
        prompt_execution_uid (int):
        model_name (Union[Unset, str]):
    """

    criteria_uid: int
    prompt_execution_uid: int
    model_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        criteria_uid = self.criteria_uid
        prompt_execution_uid = self.prompt_execution_uid
        model_name = self.model_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_uid": criteria_uid,
                "prompt_execution_uid": prompt_execution_uid,
            }
        )
        if model_name is not UNSET:
            field_dict["model_name"] = model_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        criteria_uid = d.pop("criteria_uid")

        prompt_execution_uid = d.pop("prompt_execution_uid")

        _model_name = d.pop("model_name", UNSET)
        model_name = UNSET if _model_name is None else _model_name

        obj = cls(
            criteria_uid=criteria_uid,
            prompt_execution_uid=prompt_execution_uid,
            model_name=model_name,
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
