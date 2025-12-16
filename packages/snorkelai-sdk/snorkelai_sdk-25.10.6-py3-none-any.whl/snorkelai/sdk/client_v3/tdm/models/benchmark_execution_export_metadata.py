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

from ..models.benchmark_execution_state import BenchmarkExecutionState

T = TypeVar("T", bound="BenchmarkExecutionExportMetadata")


@attrs.define
class BenchmarkExecutionExportMetadata:
    """
    Attributes:
        created_at (datetime.datetime):
        created_by (str):
        name (str):
        state (BenchmarkExecutionState):
        uid (int):
    """

    created_at: datetime.datetime
    created_by: str
    name: str
    state: BenchmarkExecutionState
    uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()
        created_by = self.created_by
        name = self.name
        state = self.state.value
        uid = self.uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "created_by": created_by,
                "name": name,
                "state": state,
                "uid": uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        created_by = d.pop("created_by")

        name = d.pop("name")

        state = BenchmarkExecutionState(d.pop("state"))

        uid = d.pop("uid")

        obj = cls(
            created_at=created_at,
            created_by=created_by,
            name=name,
            state=state,
            uid=uid,
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
