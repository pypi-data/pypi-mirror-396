from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.data_connector import DataConnector

T = TypeVar("T", bound="DataConnectorActivateRequest")


@attrs.define
class DataConnectorActivateRequest:
    """
    Attributes:
        data_connector (DataConnector):
    """

    data_connector: DataConnector
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_connector = self.data_connector.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_connector": data_connector,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_connector = DataConnector(d.pop("data_connector"))

        obj = cls(
            data_connector=data_connector,
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
