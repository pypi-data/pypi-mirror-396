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
    from ..models.label_schema_filter_structure_model import (
        LabelSchemaFilterStructureModel,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GroundTruthFilterStructureModel")


@attrs.define
class GroundTruthFilterStructureModel:
    """A wrapper around data returned to the FE to render a Ground Truth Filter options.

    Attributes:
        description (str):
        filter_type (FilterTransformFilterTypes):
        label_schemas (List['LabelSchemaFilterStructureModel']):
        name (str):
    """

    description: str
    filter_type: FilterTransformFilterTypes
    label_schemas: List["LabelSchemaFilterStructureModel"]
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_filter_structure_model import (
            LabelSchemaFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        description = self.description
        filter_type = self.filter_type.value
        label_schemas = []
        for label_schemas_item_data in self.label_schemas:
            label_schemas_item = label_schemas_item_data.to_dict()
            label_schemas.append(label_schemas_item)

        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "filter_type": filter_type,
                "label_schemas": label_schemas,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_filter_structure_model import (
            LabelSchemaFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        description = d.pop("description")

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        label_schemas = []
        _label_schemas = d.pop("label_schemas")
        for label_schemas_item_data in _label_schemas:
            label_schemas_item = LabelSchemaFilterStructureModel.from_dict(
                label_schemas_item_data
            )

            label_schemas.append(label_schemas_item)

        name = d.pop("name")

        obj = cls(
            description=description,
            filter_type=filter_type,
            label_schemas=label_schemas,
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
