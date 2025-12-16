from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.batch_data_response_grouped_data_additional_property_item import (
        BatchDataResponseGroupedDataAdditionalPropertyItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="BatchDataResponseGroupedData")


@attrs.define
class BatchDataResponseGroupedData:
    """ """

    additional_properties: Dict[
        str, List["BatchDataResponseGroupedDataAdditionalPropertyItem"]
    ] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.batch_data_response_grouped_data_additional_property_item import (
            BatchDataResponseGroupedDataAdditionalPropertyItem,  # noqa: F401
        )
        # fmt: on

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = []
            for additional_property_item_data in prop:
                additional_property_item = additional_property_item_data.to_dict()
                field_dict[prop_name].append(additional_property_item)

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.batch_data_response_grouped_data_additional_property_item import (
            BatchDataResponseGroupedDataAdditionalPropertyItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        obj = cls()
        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = []
            _additional_property = prop_dict
            for additional_property_item_data in _additional_property:
                additional_property_item = (
                    BatchDataResponseGroupedDataAdditionalPropertyItem.from_dict(
                        additional_property_item_data
                    )
                )

                additional_property.append(additional_property_item)

            additional_properties[prop_name] = additional_property

        obj.additional_properties = additional_properties
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(
        self, key: str
    ) -> List["BatchDataResponseGroupedDataAdditionalPropertyItem"]:
        return self.additional_properties[key]

    def __setitem__(
        self,
        key: str,
        value: List["BatchDataResponseGroupedDataAdditionalPropertyItem"],
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
