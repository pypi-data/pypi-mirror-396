from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="ModifySliceRequest")


@attrs.define
class ModifySliceRequest:
    """
    Attributes:
        x_uids (List[str]):
    """

    x_uids: List[str]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "x_uids": x_uids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        x_uids = cast(List[str], d.pop("x_uids"))

        obj = cls(
            x_uids=x_uids,
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
