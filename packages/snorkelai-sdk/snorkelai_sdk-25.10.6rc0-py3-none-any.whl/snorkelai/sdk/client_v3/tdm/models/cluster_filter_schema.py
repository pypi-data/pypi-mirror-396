from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClusterFilterSchema")


@attrs.define
class ClusterFilterSchema:
    """
    Attributes:
        cluster_x_uid_hash (str):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        transform_config_type (Union[Literal['cluster_filter_schema'], Unset]):  Default: 'cluster_filter_schema'.
    """

    cluster_x_uid_hash: str
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    transform_config_type: Union[Literal["cluster_filter_schema"], Unset] = (
        "cluster_filter_schema"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cluster_x_uid_hash = self.cluster_x_uid_hash
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cluster_x_uid_hash": cluster_x_uid_hash,
            }
        )
        if filter_type is not UNSET:
            field_dict["filter_type"] = filter_type
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cluster_x_uid_hash = d.pop("cluster_x_uid_hash")

        _filter_type = d.pop("filter_type", UNSET)
        _filter_type = UNSET if _filter_type is None else _filter_type
        filter_type: Union[Unset, FilterTransformFilterTypes]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = FilterTransformFilterTypes(_filter_type)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            cluster_x_uid_hash=cluster_x_uid_hash,
            filter_type=filter_type,
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
