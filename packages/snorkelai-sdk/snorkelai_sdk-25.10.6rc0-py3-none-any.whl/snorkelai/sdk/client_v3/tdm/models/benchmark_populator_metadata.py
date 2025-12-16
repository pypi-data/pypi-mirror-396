import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchmarkPopulatorMetadata")


@attrs.define
class BenchmarkPopulatorMetadata:
    """Metadata for a benchmark populator.

    Attributes:
        created_at (datetime.datetime):
        created_by_user_uid (int):
        description (str):
        name (str):
        populator_directory_name (Union[Unset, str]):
    """

    created_at: datetime.datetime
    created_by_user_uid: int
    description: str
    name: str
    populator_directory_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()
        created_by_user_uid = self.created_by_user_uid
        description = self.description
        name = self.name
        populator_directory_name = self.populator_directory_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "created_by_user_uid": created_by_user_uid,
                "description": description,
                "name": name,
            }
        )
        if populator_directory_name is not UNSET:
            field_dict["populator_directory_name"] = populator_directory_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        created_by_user_uid = d.pop("created_by_user_uid")

        description = d.pop("description")

        name = d.pop("name")

        _populator_directory_name = d.pop("populator_directory_name", UNSET)
        populator_directory_name = (
            UNSET if _populator_directory_name is None else _populator_directory_name
        )

        obj = cls(
            created_at=created_at,
            created_by_user_uid=created_by_user_uid,
            description=description,
            name=name,
            populator_directory_name=populator_directory_name,
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
