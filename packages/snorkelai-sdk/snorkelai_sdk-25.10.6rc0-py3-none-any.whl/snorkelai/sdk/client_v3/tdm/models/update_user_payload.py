from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.update_superadmin_action import UpdateSuperadminAction
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserPayload")


@attrs.define
class UpdateUserPayload:
    """
    Attributes:
        update_superadmin (Union[Unset, UpdateSuperadminAction]):
    """

    update_superadmin: Union[Unset, UpdateSuperadminAction] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        update_superadmin: Union[Unset, str] = UNSET
        if not isinstance(self.update_superadmin, Unset):
            update_superadmin = self.update_superadmin.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if update_superadmin is not UNSET:
            field_dict["update_superadmin"] = update_superadmin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _update_superadmin = d.pop("update_superadmin", UNSET)
        _update_superadmin = UNSET if _update_superadmin is None else _update_superadmin
        update_superadmin: Union[Unset, UpdateSuperadminAction]
        if isinstance(_update_superadmin, Unset):
            update_superadmin = UNSET
        else:
            update_superadmin = UpdateSuperadminAction(_update_superadmin)

        obj = cls(
            update_superadmin=update_superadmin,
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
