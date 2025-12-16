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
    from ..models.memory_profile import MemoryProfile  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="MemoryProfilingTraceResponse")


@attrs.define
class MemoryProfilingTraceResponse:
    """
    Attributes:
        profiles (List['MemoryProfile']):
    """

    profiles: List["MemoryProfile"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.memory_profile import MemoryProfile  # noqa: F401
        # fmt: on
        profiles = []
        for profiles_item_data in self.profiles:
            profiles_item = profiles_item_data.to_dict()
            profiles.append(profiles_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "profiles": profiles,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.memory_profile import MemoryProfile  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        profiles = []
        _profiles = d.pop("profiles")
        for profiles_item_data in _profiles:
            profiles_item = MemoryProfile.from_dict(profiles_item_data)

            profiles.append(profiles_item)

        obj = cls(
            profiles=profiles,
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
