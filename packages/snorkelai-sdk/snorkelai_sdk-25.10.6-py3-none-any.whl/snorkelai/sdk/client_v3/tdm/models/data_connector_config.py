from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.data_connector import DataConnector

if TYPE_CHECKING:
    # fmt: off
    from ..models.data_connector_config_config import (
        DataConnectorConfigConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DataConnectorConfig")


@attrs.define
class DataConnectorConfig:
    """
    Attributes:
        config (DataConnectorConfigConfig):
        data_connector_config_uid (int):
        data_connector_type (DataConnector):
        name (str):
        schema_version (int):
        workspace_uid (int):
    """

    config: "DataConnectorConfigConfig"
    data_connector_config_uid: int
    data_connector_type: DataConnector
    name: str
    schema_version: int
    workspace_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_connector_config_config import (
            DataConnectorConfigConfig,  # noqa: F401
        )
        # fmt: on
        config = self.config.to_dict()
        data_connector_config_uid = self.data_connector_config_uid
        data_connector_type = self.data_connector_type.value
        name = self.name
        schema_version = self.schema_version
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "data_connector_config_uid": data_connector_config_uid,
                "data_connector_type": data_connector_type,
                "name": name,
                "schema_version": schema_version,
                "workspace_uid": workspace_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_connector_config_config import (
            DataConnectorConfigConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        config = DataConnectorConfigConfig.from_dict(d.pop("config"))

        data_connector_config_uid = d.pop("data_connector_config_uid")

        data_connector_type = DataConnector(d.pop("data_connector_type"))

        name = d.pop("name")

        schema_version = d.pop("schema_version")

        workspace_uid = d.pop("workspace_uid")

        obj = cls(
            config=config,
            data_connector_config_uid=data_connector_config_uid,
            data_connector_type=data_connector_type,
            name=name,
            schema_version=schema_version,
            workspace_uid=workspace_uid,
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
