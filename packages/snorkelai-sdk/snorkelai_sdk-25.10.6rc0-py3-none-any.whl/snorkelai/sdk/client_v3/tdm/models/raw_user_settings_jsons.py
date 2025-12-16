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
    from ..models.user_settings_json import UserSettingsJson  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="RawUserSettingsJsons")


@attrs.define
class RawUserSettingsJsons:
    """
    Attributes:
        settings (List['UserSettingsJson']):
    """

    settings: List["UserSettingsJson"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.user_settings_json import UserSettingsJson  # noqa: F401
        # fmt: on
        settings = []
        for settings_item_data in self.settings:
            settings_item = settings_item_data.to_dict()
            settings.append(settings_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "settings": settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.user_settings_json import UserSettingsJson  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        settings = []
        _settings = d.pop("settings")
        for settings_item_data in _settings:
            settings_item = UserSettingsJson.from_dict(settings_item_data)

            settings.append(settings_item)

        obj = cls(
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
