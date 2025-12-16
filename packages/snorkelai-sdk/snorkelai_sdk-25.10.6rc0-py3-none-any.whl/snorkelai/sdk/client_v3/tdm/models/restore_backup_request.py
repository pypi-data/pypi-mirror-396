from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="RestoreBackupRequest")


@attrs.define
class RestoreBackupRequest:
    """
    Attributes:
        backup_id (str):
        sync (Union[Unset, bool]):  Default: True.
    """

    backup_id: str
    sync: Union[Unset, bool] = True
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        backup_id = self.backup_id
        sync = self.sync

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "backup_id": backup_id,
            }
        )
        if sync is not UNSET:
            field_dict["sync"] = sync

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        backup_id = d.pop("backup_id")

        _sync = d.pop("sync", UNSET)
        sync = UNSET if _sync is None else _sync

        obj = cls(
            backup_id=backup_id,
            sync=sync,
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
