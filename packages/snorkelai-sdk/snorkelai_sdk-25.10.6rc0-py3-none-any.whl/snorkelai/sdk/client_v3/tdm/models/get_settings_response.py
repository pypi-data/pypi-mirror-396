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
    from ..models.get_settings_response_settings import (
        GetSettingsResponseSettings,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GetSettingsResponse")


@attrs.define
class GetSettingsResponse:
    """
    Attributes:
        node_uid (int):
        settings (GetSettingsResponseSettings):
    """

    node_uid: int
    settings: "GetSettingsResponseSettings"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.get_settings_response_settings import (
            GetSettingsResponseSettings,  # noqa: F401
        )
        # fmt: on
        node_uid = self.node_uid
        settings = self.settings.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_uid": node_uid,
                "settings": settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.get_settings_response_settings import (
            GetSettingsResponseSettings,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        node_uid = d.pop("node_uid")

        settings = GetSettingsResponseSettings.from_dict(d.pop("settings"))

        obj = cls(
            node_uid=node_uid,
            settings=settings,
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
