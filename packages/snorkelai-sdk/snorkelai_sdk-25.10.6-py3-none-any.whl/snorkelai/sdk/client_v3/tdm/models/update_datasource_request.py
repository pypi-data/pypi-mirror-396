from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.split import Split
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateDatasourceRequest")


@attrs.define
class UpdateDatasourceRequest:
    """Request to update properties of a datasource.

    Attributes:
        name (Union[Unset, str]):
        split (Union[Unset, Split]): Valid dataset split types.
    """

    name: Union[Unset, str] = UNSET
    split: Union[Unset, Split] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        split: Union[Unset, str] = UNSET
        if not isinstance(self.split, Unset):
            split = self.split.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if split is not UNSET:
            field_dict["split"] = split

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _name = d.pop("name", UNSET)
        name = UNSET if _name is None else _name

        _split = d.pop("split", UNSET)
        _split = UNSET if _split is None else _split
        split: Union[Unset, Split]
        if isinstance(_split, Unset):
            split = UNSET
        else:
            split = Split(_split)

        obj = cls(
            name=name,
            split=split,
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
