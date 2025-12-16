from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.data_point_status import DataPointStatus
from ..models.filter_transform_filter_types import FilterTransformFilterTypes

T = TypeVar("T", bound="StatusFilterStructureModel")


@attrs.define
class StatusFilterStructureModel:
    """A wrapper around data returned to the FE to render a Status Filter options.

    Attributes:
        description (str):
        filter_type (FilterTransformFilterTypes):
        name (str):
        status_options (List[DataPointStatus]):
    """

    description: str
    filter_type: FilterTransformFilterTypes
    name: str
    status_options: List[DataPointStatus]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        description = self.description
        filter_type = self.filter_type.value
        name = self.name
        status_options = []
        for status_options_item_data in self.status_options:
            status_options_item = status_options_item_data.value
            status_options.append(status_options_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "filter_type": filter_type,
                "name": name,
                "status_options": status_options,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        description = d.pop("description")

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        name = d.pop("name")

        status_options = []
        _status_options = d.pop("status_options")
        for status_options_item_data in _status_options:
            status_options_item = DataPointStatus(status_options_item_data)

            status_options.append(status_options_item)

        obj = cls(
            description=description,
            filter_type=filter_type,
            name=name,
            status_options=status_options,
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
