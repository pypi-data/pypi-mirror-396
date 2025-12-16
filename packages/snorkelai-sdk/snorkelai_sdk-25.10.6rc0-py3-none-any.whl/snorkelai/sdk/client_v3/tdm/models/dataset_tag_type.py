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

T = TypeVar("T", bound="DatasetTagType")


@attrs.define
class DatasetTagType:
    """
    Attributes:
        dataset_uid (int):
        name (str):
        tag_type_uid (int):
        description (Union[Unset, str]):  Default: ''.
        is_context_tag_type (Union[Unset, bool]):  Default: False.
    """

    dataset_uid: int
    name: str
    tag_type_uid: int
    description: Union[Unset, str] = ""
    is_context_tag_type: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_uid = self.dataset_uid
        name = self.name
        tag_type_uid = self.tag_type_uid
        description = self.description
        is_context_tag_type = self.is_context_tag_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "name": name,
                "tag_type_uid": tag_type_uid,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if is_context_tag_type is not UNSET:
            field_dict["is_context_tag_type"] = is_context_tag_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        tag_type_uid = d.pop("tag_type_uid")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _is_context_tag_type = d.pop("is_context_tag_type", UNSET)
        is_context_tag_type = (
            UNSET if _is_context_tag_type is None else _is_context_tag_type
        )

        obj = cls(
            dataset_uid=dataset_uid,
            name=name,
            tag_type_uid=tag_type_uid,
            description=description,
            is_context_tag_type=is_context_tag_type,
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
