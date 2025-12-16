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

from ..models.annotator_datapoint_status import AnnotatorDatapointStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotatorAssignmentMetadata")


@attrs.define
class AnnotatorAssignmentMetadata:
    """Model for viewing annotator assignment metadata.

    Attributes:
        assigned_at (datetime.datetime):
        status (AnnotatorDatapointStatus):
        last_submitted_at (Union[Unset, datetime.datetime]):
    """

    assigned_at: datetime.datetime
    status: AnnotatorDatapointStatus
    last_submitted_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        assigned_at = self.assigned_at.isoformat()
        status = self.status.value
        last_submitted_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_submitted_at, Unset):
            last_submitted_at = self.last_submitted_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assigned_at": assigned_at,
                "status": status,
            }
        )
        if last_submitted_at is not UNSET:
            field_dict["last_submitted_at"] = last_submitted_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assigned_at = isoparse(d.pop("assigned_at"))

        status = AnnotatorDatapointStatus(d.pop("status"))

        _last_submitted_at = d.pop("last_submitted_at", UNSET)
        _last_submitted_at = UNSET if _last_submitted_at is None else _last_submitted_at
        last_submitted_at: Union[Unset, datetime.datetime]
        if isinstance(_last_submitted_at, Unset):
            last_submitted_at = UNSET
        else:
            last_submitted_at = isoparse(_last_submitted_at)

        obj = cls(
            assigned_at=assigned_at,
            status=status,
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
