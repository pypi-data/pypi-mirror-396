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

T = TypeVar("T", bound="ViewConfig")


@attrs.define
class ViewConfig:
    """
    Attributes:
        text_direction (Union[Unset, str]):
        with_auto_advance (Union[Unset, bool]):
    """

    text_direction: Union[Unset, str] = UNSET
    with_auto_advance: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        text_direction = self.text_direction
        with_auto_advance = self.with_auto_advance

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text_direction is not UNSET:
            field_dict["text_direction"] = text_direction
        if with_auto_advance is not UNSET:
            field_dict["with_auto_advance"] = with_auto_advance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _text_direction = d.pop("text_direction", UNSET)
        text_direction = UNSET if _text_direction is None else _text_direction

        _with_auto_advance = d.pop("with_auto_advance", UNSET)
        with_auto_advance = UNSET if _with_auto_advance is None else _with_auto_advance

        obj = cls(
            text_direction=text_direction,
            with_auto_advance=with_auto_advance,
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
