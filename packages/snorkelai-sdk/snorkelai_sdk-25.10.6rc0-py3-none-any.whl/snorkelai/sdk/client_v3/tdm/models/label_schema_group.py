from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="LabelSchemaGroup")


@attrs.define
class LabelSchemaGroup:
    """
    Attributes:
        name (str): Display name for this group of related label schemas
        description (Union[Unset, str]): Description for this group of related label schemas
        label_schema_uids (Union[Unset, List[int]]): List of label_schema_uids in this group
    """

    name: str
    description: Union[Unset, str] = UNSET
    label_schema_uids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        description = self.description
        label_schema_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.label_schema_uids, Unset):
            label_schema_uids = self.label_schema_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if label_schema_uids is not UNSET:
            field_dict["label_schema_uids"] = label_schema_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _label_schema_uids = d.pop("label_schema_uids", UNSET)
        label_schema_uids = cast(
            List[int], UNSET if _label_schema_uids is None else _label_schema_uids
        )

        obj = cls(
            name=name,
            description=description,
            label_schema_uids=label_schema_uids,
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
