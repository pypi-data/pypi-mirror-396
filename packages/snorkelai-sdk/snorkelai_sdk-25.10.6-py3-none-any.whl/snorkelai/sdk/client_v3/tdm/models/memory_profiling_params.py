from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.persistence_mode import PersistenceMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="MemoryProfilingParams")


@attrs.define
class MemoryProfilingParams:
    """
    Attributes:
        service (str):
        persistence_mode (Union[Unset, PersistenceMode]):
    """

    service: str
    persistence_mode: Union[Unset, PersistenceMode] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        service = self.service
        persistence_mode: Union[Unset, str] = UNSET
        if not isinstance(self.persistence_mode, Unset):
            persistence_mode = self.persistence_mode.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
            }
        )
        if persistence_mode is not UNSET:
            field_dict["persistence_mode"] = persistence_mode

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        service = d.pop("service")

        _persistence_mode = d.pop("persistence_mode", UNSET)
        _persistence_mode = UNSET if _persistence_mode is None else _persistence_mode
        persistence_mode: Union[Unset, PersistenceMode]
        if isinstance(_persistence_mode, Unset):
            persistence_mode = UNSET
        else:
            persistence_mode = PersistenceMode(_persistence_mode)

        obj = cls(
            service=service,
            persistence_mode=persistence_mode,
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
