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
from ..models.slice_filter_operator import SliceFilterOperator
from ..types import UNSET, Unset

T = TypeVar("T", bound="SliceFilterSchema")


@attrs.define
class SliceFilterSchema:
    """
    Attributes:
        operator (SliceFilterOperator):
        slice_uid (int):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        transform_config_type (Union[Literal['slice_filter_schema'], Unset]):  Default: 'slice_filter_schema'.
    """

    operator: SliceFilterOperator
    slice_uid: int
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    transform_config_type: Union[Literal["slice_filter_schema"], Unset] = (
        "slice_filter_schema"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        operator = self.operator.value
        slice_uid = self.slice_uid
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "operator": operator,
                "slice_uid": slice_uid,
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
        operator = SliceFilterOperator(d.pop("operator"))

        slice_uid = d.pop("slice_uid")

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
            operator=operator,
            slice_uid=slice_uid,
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
