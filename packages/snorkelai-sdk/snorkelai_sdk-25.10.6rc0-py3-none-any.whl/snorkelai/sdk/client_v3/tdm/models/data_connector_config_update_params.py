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
    from ..models.data_connector_config_update_params_new_config import (
        DataConnectorConfigUpdateParamsNewConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DataConnectorConfigUpdateParams")


@attrs.define
class DataConnectorConfigUpdateParams:
    """
    Attributes:
        new_config (DataConnectorConfigUpdateParamsNewConfig):
        new_name (str):
    """

    new_config: "DataConnectorConfigUpdateParamsNewConfig"
    new_name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_connector_config_update_params_new_config import (
            DataConnectorConfigUpdateParamsNewConfig,  # noqa: F401
        )
        # fmt: on
        new_config = self.new_config.to_dict()
        new_name = self.new_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_config": new_config,
                "new_name": new_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_connector_config_update_params_new_config import (
            DataConnectorConfigUpdateParamsNewConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        new_config = DataConnectorConfigUpdateParamsNewConfig.from_dict(
            d.pop("new_config")
        )

        new_name = d.pop("new_name")

        obj = cls(
            new_config=new_config,
            new_name=new_name,
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
