from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes

if TYPE_CHECKING:
    # fmt: off
    from ..models.option_model import OptionModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SliceFilterStructureModel")


@attrs.define
class SliceFilterStructureModel:
    """A wrapper around data returned to the FE to render slice Filter options.

    Attributes:
        description (str):
        filter_type (FilterTransformFilterTypes):
        name (str):
        operators (List[str]):
        slices (List['OptionModel']):
    """

    description: str
    filter_type: FilterTransformFilterTypes
    name: str
    operators: List[str]
    slices: List["OptionModel"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        description = self.description
        filter_type = self.filter_type.value
        name = self.name
        operators = self.operators

        slices = []
        for slices_item_data in self.slices:
            slices_item = slices_item_data.to_dict()
            slices.append(slices_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "filter_type": filter_type,
                "name": name,
                "operators": operators,
                "slices": slices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        description = d.pop("description")

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        name = d.pop("name")

        operators = cast(List[str], d.pop("operators"))

        slices = []
        _slices = d.pop("slices")
        for slices_item_data in _slices:
            slices_item = OptionModel.from_dict(slices_item_data)

            slices.append(slices_item)

        obj = cls(
            description=description,
            filter_type=filter_type,
            name=name,
            operators=operators,
            slices=slices,
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
