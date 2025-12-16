from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.filter_transform import FilterTransform  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FilterCondition")


@attrs.define
class FilterCondition:
    """A filter condition maps a data point to a boolean of whether the condition applies

    This is the primary logic for a filter.
    Note that a Filter condition may be composed of one or more conditions being combined.

        Attributes:
            conditions (List[Union['FilterCondition', 'FilterTransform']]):
            op_name (str):
    """

    conditions: List[Union["FilterCondition", "FilterTransform"]]
    op_name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.filter_transform import FilterTransform  # noqa: F401
        # fmt: on
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item: Dict[str, Any]
            if isinstance(conditions_item_data, FilterTransform):
                conditions_item = conditions_item_data.to_dict()
            else:
                conditions_item = conditions_item_data.to_dict()

            conditions.append(conditions_item)

        op_name = self.op_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
                "op_name": op_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.filter_transform import FilterTransform  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:

            def _parse_conditions_item(
                data: object,
            ) -> Union["FilterCondition", "FilterTransform"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    conditions_item_type_0 = FilterTransform.from_dict(data)

                    return conditions_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                conditions_item_type_1 = FilterCondition.from_dict(data)

                return conditions_item_type_1

            conditions_item = _parse_conditions_item(conditions_item_data)

            conditions.append(conditions_item)

        op_name = d.pop("op_name")

        obj = cls(
            conditions=conditions,
            op_name=op_name,
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
