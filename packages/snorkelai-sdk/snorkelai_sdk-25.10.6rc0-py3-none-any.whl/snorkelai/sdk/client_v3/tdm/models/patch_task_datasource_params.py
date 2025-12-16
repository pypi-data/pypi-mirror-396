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

T = TypeVar("T", bound="PatchTaskDatasourceParams")


@attrs.define
class PatchTaskDatasourceParams:
    """
    Attributes:
        is_active (Union[Unset, bool]):
        supports_dev (Union[Unset, bool]):
    """

    is_active: Union[Unset, bool] = UNSET
    supports_dev: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        is_active = self.is_active
        supports_dev = self.supports_dev

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if supports_dev is not UNSET:
            field_dict["supports_dev"] = supports_dev

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _is_active = d.pop("is_active", UNSET)
        is_active = UNSET if _is_active is None else _is_active

        _supports_dev = d.pop("supports_dev", UNSET)
        supports_dev = UNSET if _supports_dev is None else _supports_dev

        obj = cls(
            is_active=is_active,
            supports_dev=supports_dev,
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
