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

T = TypeVar("T", bound="SubmitAnnotationTaskResponse")


@attrs.define
class SubmitAnnotationTaskResponse:
    """Response model for submit_annotation_task_status function.

    Attributes:
        assigned_at (datetime.datetime):
        last_submitted_at (datetime.datetime):
    """

    assigned_at: datetime.datetime
    last_submitted_at: datetime.datetime
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        assigned_at = self.assigned_at.isoformat()
        last_submitted_at = self.last_submitted_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assigned_at": assigned_at,
                "last_submitted_at": last_submitted_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assigned_at = isoparse(d.pop("assigned_at"))

        last_submitted_at = isoparse(d.pop("last_submitted_at"))

        obj = cls(
            assigned_at=assigned_at,
            last_submitted_at=last_submitted_at,
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
