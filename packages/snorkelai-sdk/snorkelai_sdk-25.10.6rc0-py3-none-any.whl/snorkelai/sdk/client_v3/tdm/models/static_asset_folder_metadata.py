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

T = TypeVar("T", bound="StaticAssetFolderMetadata")


@attrs.define
class StaticAssetFolderMetadata:
    """
    Attributes:
        asset_types (List[str]):
        path (str):
        is_folder (Union[Unset, bool]):  Default: True.
        size_bytes (Union[Unset, int]):
    """

    asset_types: List[str]
    path: str
    is_folder: Union[Unset, bool] = True
    size_bytes: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        asset_types = self.asset_types

        path = self.path
        is_folder = self.is_folder
        size_bytes = self.size_bytes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "asset_types": asset_types,
                "path": path,
            }
        )
        if is_folder is not UNSET:
            field_dict["is_folder"] = is_folder
        if size_bytes is not UNSET:
            field_dict["size_bytes"] = size_bytes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        asset_types = cast(List[str], d.pop("asset_types"))

        path = d.pop("path")

        _is_folder = d.pop("is_folder", UNSET)
        is_folder = UNSET if _is_folder is None else _is_folder

        _size_bytes = d.pop("size_bytes", UNSET)
        size_bytes = UNSET if _size_bytes is None else _size_bytes

        obj = cls(
            asset_types=asset_types,
            path=path,
            is_folder=is_folder,
            size_bytes=size_bytes,
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
