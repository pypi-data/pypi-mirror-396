from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="FileStorageConfig")


@attrs.define
class FileStorageConfig:
    """
    Attributes:
        base_path (str):
        file_storage_config_uid (int):
        is_default (bool):
        name (str):
    """

    base_path: str
    file_storage_config_uid: int
    is_default: bool
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base_path = self.base_path
        file_storage_config_uid = self.file_storage_config_uid
        is_default = self.is_default
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_path": base_path,
                "file_storage_config_uid": file_storage_config_uid,
                "is_default": is_default,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        base_path = d.pop("base_path")

        file_storage_config_uid = d.pop("file_storage_config_uid")

        is_default = d.pop("is_default")

        name = d.pop("name")

        obj = cls(
            base_path=base_path,
            file_storage_config_uid=file_storage_config_uid,
            is_default=is_default,
            name=name,
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
