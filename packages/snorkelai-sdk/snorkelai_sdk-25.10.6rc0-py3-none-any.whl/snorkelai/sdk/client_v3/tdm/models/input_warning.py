from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.warning_action import WarningAction
from ..models.warning_level import WarningLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="InputWarning")


@attrs.define
class InputWarning:
    """
    Attributes:
        level (WarningLevel):
        text (str):
        action (Union[Unset, WarningAction]):
        column (Union[Unset, str]):
        stacktrace (Union[Unset, str]):
    """

    level: WarningLevel
    text: str
    action: Union[Unset, WarningAction] = UNSET
    column: Union[Unset, str] = UNSET
    stacktrace: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        level = self.level.value
        text = self.text
        action: Union[Unset, str] = UNSET
        if not isinstance(self.action, Unset):
            action = self.action.value

        column = self.column
        stacktrace = self.stacktrace

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level": level,
                "text": text,
            }
        )
        if action is not UNSET:
            field_dict["action"] = action
        if column is not UNSET:
            field_dict["column"] = column
        if stacktrace is not UNSET:
            field_dict["stacktrace"] = stacktrace

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        level = WarningLevel(d.pop("level"))

        text = d.pop("text")

        _action = d.pop("action", UNSET)
        _action = UNSET if _action is None else _action
        action: Union[Unset, WarningAction]
        if isinstance(_action, Unset):
            action = UNSET
        else:
            action = WarningAction(_action)

        _column = d.pop("column", UNSET)
        column = UNSET if _column is None else _column

        _stacktrace = d.pop("stacktrace", UNSET)
        stacktrace = UNSET if _stacktrace is None else _stacktrace

        obj = cls(
            level=level,
            text=text,
            action=action,
            column=column,
            stacktrace=stacktrace,
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
