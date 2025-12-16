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

T = TypeVar("T", bound="GlobalPreferences")


@attrs.define
class GlobalPreferences:
    """
    Attributes:
        created_by_me_filter (Union[Unset, bool]):
        enable_notifications (Union[Unset, bool]):
        saved_workspace (Union[Unset, int]):
    """

    created_by_me_filter: Union[Unset, bool] = UNSET
    enable_notifications: Union[Unset, bool] = UNSET
    saved_workspace: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_by_me_filter = self.created_by_me_filter
        enable_notifications = self.enable_notifications
        saved_workspace = self.saved_workspace

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_by_me_filter is not UNSET:
            field_dict["created_by_me_filter"] = created_by_me_filter
        if enable_notifications is not UNSET:
            field_dict["enable_notifications"] = enable_notifications
        if saved_workspace is not UNSET:
            field_dict["saved_workspace"] = saved_workspace

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _created_by_me_filter = d.pop("created_by_me_filter", UNSET)
        created_by_me_filter = (
            UNSET if _created_by_me_filter is None else _created_by_me_filter
        )

        _enable_notifications = d.pop("enable_notifications", UNSET)
        enable_notifications = (
            UNSET if _enable_notifications is None else _enable_notifications
        )

        _saved_workspace = d.pop("saved_workspace", UNSET)
        saved_workspace = UNSET if _saved_workspace is None else _saved_workspace

        obj = cls(
            created_by_me_filter=created_by_me_filter,
            enable_notifications=enable_notifications,
            saved_workspace=saved_workspace,
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
