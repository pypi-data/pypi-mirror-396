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

T = TypeVar("T", bound="CreateOrUpdateCodePayload")


@attrs.define
class CreateOrUpdateCodePayload:
    """
    Attributes:
        code (str):
        code_version_name (Union[Unset, str]):
    """

    code: str
    code_version_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code = self.code
        code_version_name = self.code_version_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
            }
        )
        if code_version_name is not UNSET:
            field_dict["code_version_name"] = code_version_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code = d.pop("code")

        _code_version_name = d.pop("code_version_name", UNSET)
        code_version_name = UNSET if _code_version_name is None else _code_version_name

        obj = cls(
            code=code,
            code_version_name=code_version_name,
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
