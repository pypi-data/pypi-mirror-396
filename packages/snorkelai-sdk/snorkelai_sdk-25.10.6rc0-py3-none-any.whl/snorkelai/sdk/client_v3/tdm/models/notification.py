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

from ..models.notification_type import NotificationType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.notification_body import NotificationBody  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Notification")


@attrs.define
class Notification:
    """
    Attributes:
        body (NotificationBody):
        created_at (datetime.datetime):
        notification_type (NotificationType):
        notification_uid (int):
        user_uid (int):
        is_read (Union[Unset, bool]):  Default: False.
    """

    body: "NotificationBody"
    created_at: datetime.datetime
    notification_type: NotificationType
    notification_uid: int
    user_uid: int
    is_read: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.notification_body import NotificationBody  # noqa: F401
        # fmt: on
        body = self.body.to_dict()
        created_at = self.created_at.isoformat()
        notification_type = self.notification_type.value
        notification_uid = self.notification_uid
        user_uid = self.user_uid
        is_read = self.is_read

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
                "created_at": created_at,
                "notification_type": notification_type,
                "notification_uid": notification_uid,
                "user_uid": user_uid,
            }
        )
        if is_read is not UNSET:
            field_dict["is_read"] = is_read

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.notification_body import NotificationBody  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        body = NotificationBody.from_dict(d.pop("body"))

        created_at = isoparse(d.pop("created_at"))

        notification_type = NotificationType(d.pop("notification_type"))

        notification_uid = d.pop("notification_uid")

        user_uid = d.pop("user_uid")

        _is_read = d.pop("is_read", UNSET)
        is_read = UNSET if _is_read is None else _is_read

        obj = cls(
            body=body,
            created_at=created_at,
            notification_type=notification_type,
            notification_uid=notification_uid,
            user_uid=user_uid,
            is_read=is_read,
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
