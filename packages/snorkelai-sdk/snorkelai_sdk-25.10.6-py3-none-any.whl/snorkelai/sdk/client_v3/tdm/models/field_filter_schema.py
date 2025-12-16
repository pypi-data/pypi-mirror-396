from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldFilterSchema")


@attrs.define
class FieldFilterSchema:
    """
    Attributes:
        field (str):
        operator (str):
        value (Union[float, str]):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        transform_config_type (Union[Literal['field_filter_schema'], Unset]):  Default: 'field_filter_schema'.
        use_annotation_datasources (Union[Unset, bool]):  Default: True.
    """

    field: str
    operator: str
    value: Union[float, str]
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    transform_config_type: Union[Literal["field_filter_schema"], Unset] = (
        "field_filter_schema"
    )
    use_annotation_datasources: Union[Unset, bool] = True
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        field = self.field
        operator = self.operator
        value: Union[float, str]
        value = self.value
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        transform_config_type = self.transform_config_type
        use_annotation_datasources = self.use_annotation_datasources

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "operator": operator,
                "value": value,
            }
        )
        if filter_type is not UNSET:
            field_dict["filter_type"] = filter_type
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type
        if use_annotation_datasources is not UNSET:
            field_dict["use_annotation_datasources"] = use_annotation_datasources

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        field = d.pop("field")

        operator = d.pop("operator")

        def _parse_value(data: object) -> Union[float, str]:
            return cast(Union[float, str], data)

        value = _parse_value(d.pop("value"))

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

        _use_annotation_datasources = d.pop("use_annotation_datasources", UNSET)
        use_annotation_datasources = (
            UNSET
            if _use_annotation_datasources is None
            else _use_annotation_datasources
        )

        obj = cls(
            field=field,
            operator=operator,
            value=value,
            filter_type=filter_type,
            transform_config_type=transform_config_type,
            use_annotation_datasources=use_annotation_datasources,
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
