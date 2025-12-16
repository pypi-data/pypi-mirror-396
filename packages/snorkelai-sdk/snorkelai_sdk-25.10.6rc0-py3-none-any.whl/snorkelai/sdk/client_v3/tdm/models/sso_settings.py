from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.sso_type import SsoType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SsoSettings")


@attrs.define
class SsoSettings:
    """
    Attributes:
        sso_enabled (bool):
        sso_required (bool):
        sso_type (Union[Unset, SsoType]):
    """

    sso_enabled: bool
    sso_required: bool
    sso_type: Union[Unset, SsoType] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sso_enabled = self.sso_enabled
        sso_required = self.sso_required
        sso_type: Union[Unset, str] = UNSET
        if not isinstance(self.sso_type, Unset):
            sso_type = self.sso_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sso_enabled": sso_enabled,
                "sso_required": sso_required,
            }
        )
        if sso_type is not UNSET:
            field_dict["sso_type"] = sso_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sso_enabled = d.pop("sso_enabled")

        sso_required = d.pop("sso_required")

        _sso_type = d.pop("sso_type", UNSET)
        _sso_type = UNSET if _sso_type is None else _sso_type
        sso_type: Union[Unset, SsoType]
        if isinstance(_sso_type, Unset):
            sso_type = UNSET
        else:
            sso_type = SsoType(_sso_type)

        obj = cls(
            sso_enabled=sso_enabled,
            sso_required=sso_required,
            sso_type=sso_type,
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
