import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs
from dateutil.parser import isoparse

T = TypeVar("T", bound="DatasetInfo")


@attrs.define
class DatasetInfo:
    """
    Attributes:
        dataset_uid (int):
        last_viewed_at (datetime.datetime):
        name (str):
        total_size_bytes (int):
        workspace_uid (int):
    """

    dataset_uid: int
    last_viewed_at: datetime.datetime
    name: str
    total_size_bytes: int
    workspace_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_uid = self.dataset_uid
        last_viewed_at = self.last_viewed_at.isoformat()
        name = self.name
        total_size_bytes = self.total_size_bytes
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "last_viewed_at": last_viewed_at,
                "name": name,
                "total_size_bytes": total_size_bytes,
                "workspace_uid": workspace_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        last_viewed_at = isoparse(d.pop("last_viewed_at"))

        name = d.pop("name")

        total_size_bytes = d.pop("total_size_bytes")

        workspace_uid = d.pop("workspace_uid")

        obj = cls(
            dataset_uid=dataset_uid,
            last_viewed_at=last_viewed_at,
            name=name,
            total_size_bytes=total_size_bytes,
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
