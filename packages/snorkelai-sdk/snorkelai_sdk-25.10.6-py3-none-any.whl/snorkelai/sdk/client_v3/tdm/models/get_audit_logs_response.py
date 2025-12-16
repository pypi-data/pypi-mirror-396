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
    from ..models.audit_event import AuditEvent  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetAuditLogsResponse")


@attrs.define
class GetAuditLogsResponse:
    """
    Attributes:
        events (List['AuditEvent']):
        last_id (int):
    """

    events: List["AuditEvent"]
    last_id: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.audit_event import AuditEvent  # noqa: F401
        # fmt: on
        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        last_id = self.last_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "events": events,
                "last_id": last_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.audit_event import AuditEvent  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = AuditEvent.from_dict(events_item_data)

            events.append(events_item)

        last_id = d.pop("last_id")

        obj = cls(
            events=events,
            last_id=last_id,
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
