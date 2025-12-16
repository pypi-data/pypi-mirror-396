import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..models.event_type import EventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.audit_event_event_details import AuditEventEventDetails  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AuditEvent")


@attrs.define
class AuditEvent:
    """
    Attributes:
        event_id (int):
        event_name (str):
        event_type (EventType):
        authentication_method (Union[Unset, str]):
        event_details (Union[Unset, AuditEventEventDetails]):
        event_time (Union[Unset, datetime.datetime]):
        user_uid (Union[Unset, int]):
    """

    event_id: int
    event_name: str
    event_type: EventType
    authentication_method: Union[Unset, str] = UNSET
    event_details: Union[Unset, "AuditEventEventDetails"] = UNSET
    event_time: Union[Unset, datetime.datetime] = UNSET
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.audit_event_event_details import (
            AuditEventEventDetails,  # noqa: F401
        )
        # fmt: on
        event_id = self.event_id
        event_name = self.event_name
        event_type = self.event_type.value
        authentication_method = self.authentication_method
        event_details: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.event_details, Unset):
            event_details = self.event_details.to_dict()
        event_time: Union[Unset, str] = UNSET
        if not isinstance(self.event_time, Unset):
            event_time = self.event_time.isoformat()
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_id": event_id,
                "event_name": event_name,
                "event_type": event_type,
            }
        )
        if authentication_method is not UNSET:
            field_dict["authentication_method"] = authentication_method
        if event_details is not UNSET:
            field_dict["event_details"] = event_details
        if event_time is not UNSET:
            field_dict["event_time"] = event_time
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.audit_event_event_details import (
            AuditEventEventDetails,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        event_id = d.pop("event_id")

        event_name = d.pop("event_name")

        event_type = EventType(d.pop("event_type"))

        _authentication_method = d.pop("authentication_method", UNSET)
        authentication_method = (
            UNSET if _authentication_method is None else _authentication_method
        )

        _event_details = d.pop("event_details", UNSET)
        _event_details = UNSET if _event_details is None else _event_details
        event_details: Union[Unset, AuditEventEventDetails]
        if isinstance(_event_details, Unset):
            event_details = UNSET
        else:
            event_details = AuditEventEventDetails.from_dict(_event_details)

        _event_time = d.pop("event_time", UNSET)
        _event_time = UNSET if _event_time is None else _event_time
        event_time: Union[Unset, datetime.datetime]
        if isinstance(_event_time, Unset):
            event_time = UNSET
        else:
            event_time = isoparse(_event_time)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            event_id=event_id,
            event_name=event_name,
            event_type=event_type,
            authentication_method=authentication_method,
            event_details=event_details,
            event_time=event_time,
            user_uid=user_uid,
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
