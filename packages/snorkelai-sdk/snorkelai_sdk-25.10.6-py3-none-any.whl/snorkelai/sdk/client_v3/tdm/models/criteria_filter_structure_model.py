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
    from ..models.criteria_fields_model import CriteriaFieldsModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CriteriaFilterStructureModel")


@attrs.define
class CriteriaFilterStructureModel:
    """A wrapper around data returned to the FE to render criteria Filter options.

    Attributes:
        criteria_fields (List['CriteriaFieldsModel']):
        description (str):
        filter_type (FilterTransformFilterTypes):
        name (str):
    """

    criteria_fields: List["CriteriaFieldsModel"]
    description: str
    filter_type: FilterTransformFilterTypes
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.criteria_fields_model import CriteriaFieldsModel  # noqa: F401
        # fmt: on
        criteria_fields = []
        for criteria_fields_item_data in self.criteria_fields:
            criteria_fields_item = criteria_fields_item_data.to_dict()
            criteria_fields.append(criteria_fields_item)

        description = self.description
        filter_type = self.filter_type.value
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_fields": criteria_fields,
                "description": description,
                "filter_type": filter_type,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.criteria_fields_model import CriteriaFieldsModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        criteria_fields = []
        _criteria_fields = d.pop("criteria_fields")
        for criteria_fields_item_data in _criteria_fields:
            criteria_fields_item = CriteriaFieldsModel.from_dict(
                criteria_fields_item_data
            )

            criteria_fields.append(criteria_fields_item)

        description = d.pop("description")

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        name = d.pop("name")

        obj = cls(
            criteria_fields=criteria_fields,
            description=description,
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
