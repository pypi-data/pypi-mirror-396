from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="CreateSelectedDefaultCriteriaPayload")


@attrs.define
class CreateSelectedDefaultCriteriaPayload:
    """
    Attributes:
        selected_criteria_names (List[str]):
    """

    selected_criteria_names: List[str]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selected_criteria_names = self.selected_criteria_names

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "selected_criteria_names": selected_criteria_names,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        selected_criteria_names = cast(List[str], d.pop("selected_criteria_names"))

        obj = cls(
            selected_criteria_names=selected_criteria_names,
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
