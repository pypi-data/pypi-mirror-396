from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.dataset_transform_config_types import DatasetTransformConfigTypes

T = TypeVar("T", bound="DatasetTransformConfig")


@attrs.define
class DatasetTransformConfig:
    """
    Attributes:
        transform_config_type (DatasetTransformConfigTypes):
    """

    transform_config_type: DatasetTransformConfigTypes
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        transform_config_type = self.transform_config_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transform_config_type": transform_config_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        transform_config_type = DatasetTransformConfigTypes(
            d.pop("transform_config_type")
        )

        obj = cls(
            transform_config_type=transform_config_type,
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
