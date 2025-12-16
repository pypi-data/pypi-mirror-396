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

from ..types import UNSET, Unset

T = TypeVar("T", bound="FilterStringConfig")


@attrs.define
class FilterStringConfig:
    """
    Attributes:
        filter_string (str):
        transform_config_type (Union[Literal['filter_string'], Unset]):  Default: 'filter_string'.
    """

    filter_string: str
    transform_config_type: Union[Literal["filter_string"], Unset] = "filter_string"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_string = self.filter_string
        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filter_string": filter_string,
            }
        )
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        filter_string = d.pop("filter_string")

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            filter_string=filter_string,
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
