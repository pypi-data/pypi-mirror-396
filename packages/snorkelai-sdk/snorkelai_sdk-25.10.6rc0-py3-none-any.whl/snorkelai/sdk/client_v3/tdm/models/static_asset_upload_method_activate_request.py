from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.static_asset_upload_method import StaticAssetUploadMethod

T = TypeVar("T", bound="StaticAssetUploadMethodActivateRequest")


@attrs.define
class StaticAssetUploadMethodActivateRequest:
    """
    Attributes:
        static_asset_upload_method (StaticAssetUploadMethod):
    """

    static_asset_upload_method: StaticAssetUploadMethod
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        static_asset_upload_method = self.static_asset_upload_method.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "static_asset_upload_method": static_asset_upload_method,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        static_asset_upload_method = StaticAssetUploadMethod(
            d.pop("static_asset_upload_method")
        )

        obj = cls(
            static_asset_upload_method=static_asset_upload_method,
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
