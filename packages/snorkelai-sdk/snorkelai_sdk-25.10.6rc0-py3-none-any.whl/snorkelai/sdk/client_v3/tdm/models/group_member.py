from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroupMember")


@attrs.define
class GroupMember:
    """
    Attributes:
        display (Union[Unset, str]):
        primary (Union[Unset, bool]): A Boolean value indicating the 'primary' or preferred attribute value
            for this attribute.
        ref (Union[Unset, str]): The reference URI of a target resource, if the attribute is a
            reference.
        type (Union[Unset, str]): A label indicating the attribute's function, e.g., "work" or "home".
        value (Union[Unset, str]): Identifier of the member of this Group.
    """

    display: Union[Unset, str] = UNSET
    primary: Union[Unset, bool] = UNSET
    ref: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    value: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        display = self.display
        primary = self.primary
        ref = self.ref
        type = self.type
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if display is not UNSET:
            field_dict["display"] = display
        if primary is not UNSET:
            field_dict["primary"] = primary
        if ref is not UNSET:
            field_dict["ref"] = ref
        if type is not UNSET:
            field_dict["type"] = type
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _display = d.pop("display", UNSET)
        display = UNSET if _display is None else _display

        _primary = d.pop("primary", UNSET)
        primary = UNSET if _primary is None else _primary

        _ref = d.pop("ref", UNSET)
        ref = UNSET if _ref is None else _ref

        _type = d.pop("type", UNSET)
        type = UNSET if _type is None else _type

        _value = d.pop("value", UNSET)
        value = UNSET if _value is None else _value

        obj = cls(
            display=display,
            primary=primary,
            ref=ref,
            type=type,
            value=value,
        )
        return obj
