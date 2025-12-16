from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes

if TYPE_CHECKING:
    # fmt: off
    from ..models.fields_model import FieldsModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FieldFilterStructureModel")


@attrs.define
class FieldFilterStructureModel:
    """A wrapper around data returned to the FE to render a Field Filter options.

    Attributes:
        description (str):
        fields (List['FieldsModel']):
        filter_type (FilterTransformFilterTypes):
        name (str):
    """

    description: str
    fields: List["FieldsModel"]
    filter_type: FilterTransformFilterTypes
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.fields_model import FieldsModel  # noqa: F401
        # fmt: on
        description = self.description
        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        filter_type = self.filter_type.value
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "fields": fields,
                "filter_type": filter_type,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.fields_model import FieldsModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        description = d.pop("description")

        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = FieldsModel.from_dict(fields_item_data)

            fields.append(fields_item)

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        name = d.pop("name")

        obj = cls(
            description=description,
            fields=fields,
            filter_type=filter_type,
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
