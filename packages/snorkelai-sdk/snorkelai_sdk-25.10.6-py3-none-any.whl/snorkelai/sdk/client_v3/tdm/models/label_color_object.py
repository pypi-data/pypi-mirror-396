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

T = TypeVar("T", bound="LabelColorObject")


@attrs.define
class LabelColorObject:
    """
    Attributes:
        label_background_color (Union[Unset, str]):
        label_text_color (Union[Unset, str]):
    """

    label_background_color: Union[Unset, str] = UNSET
    label_text_color: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label_background_color = self.label_background_color
        label_text_color = self.label_text_color

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if label_background_color is not UNSET:
            field_dict["label_background_color"] = label_background_color
        if label_text_color is not UNSET:
            field_dict["label_text_color"] = label_text_color

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _label_background_color = d.pop("label_background_color", UNSET)
        label_background_color = (
            UNSET if _label_background_color is None else _label_background_color
        )

        _label_text_color = d.pop("label_text_color", UNSET)
        label_text_color = UNSET if _label_text_color is None else _label_text_color

        obj = cls(
            label_background_color=label_background_color,
            label_text_color=label_text_color,
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
