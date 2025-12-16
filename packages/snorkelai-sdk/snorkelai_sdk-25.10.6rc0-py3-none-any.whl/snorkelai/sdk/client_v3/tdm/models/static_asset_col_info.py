from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.asset_upload_type import AssetUploadType
from ..models.remote_storage_type import RemoteStorageType

T = TypeVar("T", bound="StaticAssetColInfo")


@attrs.define
class StaticAssetColInfo:
    """
    Attributes:
        datasource_reference_col_name (str):
        remote_storage_type (RemoteStorageType):
        resize_image (bool):
        static_asset_col_name (str):
        static_asset_file_type (AssetUploadType):
        storage_path (str):
    """

    datasource_reference_col_name: str
    remote_storage_type: RemoteStorageType
    resize_image: bool
    static_asset_col_name: str
    static_asset_file_type: AssetUploadType
    storage_path: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        datasource_reference_col_name = self.datasource_reference_col_name
        remote_storage_type = self.remote_storage_type.value
        resize_image = self.resize_image
        static_asset_col_name = self.static_asset_col_name
        static_asset_file_type = self.static_asset_file_type.value
        storage_path = self.storage_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasource_reference_col_name": datasource_reference_col_name,
                "remote_storage_type": remote_storage_type,
                "resize_image": resize_image,
                "static_asset_col_name": static_asset_col_name,
                "static_asset_file_type": static_asset_file_type,
                "storage_path": storage_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        datasource_reference_col_name = d.pop("datasource_reference_col_name")

        remote_storage_type = RemoteStorageType(d.pop("remote_storage_type"))

        resize_image = d.pop("resize_image")

        static_asset_col_name = d.pop("static_asset_col_name")

        static_asset_file_type = AssetUploadType(d.pop("static_asset_file_type"))

        storage_path = d.pop("storage_path")

        obj = cls(
            datasource_reference_col_name=datasource_reference_col_name,
            remote_storage_type=remote_storage_type,
            resize_image=resize_image,
            static_asset_col_name=static_asset_col_name,
            static_asset_file_type=static_asset_file_type,
            storage_path=storage_path,
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
