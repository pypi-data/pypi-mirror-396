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

T = TypeVar("T", bound="CreateCriteriaTemplateFromCriteriaRequest")


@attrs.define
class CreateCriteriaTemplateFromCriteriaRequest:
    """
    Attributes:
        criteria_template_name (str):
        prompt_uid (int):
        criteria_template_description (Union[Unset, str]):
    """

    criteria_template_name: str
    prompt_uid: int
    criteria_template_description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        criteria_template_name = self.criteria_template_name
        prompt_uid = self.prompt_uid
        criteria_template_description = self.criteria_template_description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_template_name": criteria_template_name,
                "prompt_uid": prompt_uid,
            }
        )
        if criteria_template_description is not UNSET:
            field_dict["criteria_template_description"] = criteria_template_description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        criteria_template_name = d.pop("criteria_template_name")

        prompt_uid = d.pop("prompt_uid")

        _criteria_template_description = d.pop("criteria_template_description", UNSET)
        criteria_template_description = (
            UNSET
            if _criteria_template_description is None
            else _criteria_template_description
        )

        obj = cls(
            criteria_template_name=criteria_template_name,
            prompt_uid=prompt_uid,
            criteria_template_description=criteria_template_description,
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
