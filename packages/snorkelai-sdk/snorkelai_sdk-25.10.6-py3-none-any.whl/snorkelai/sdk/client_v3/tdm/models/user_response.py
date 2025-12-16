from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.user_role import UserRole
from ..models.user_view import UserView
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserResponse")


@attrs.define
class UserResponse:
    """
    Attributes:
        default_view (UserView):
        is_active (bool):
        is_locked (bool):
        role (UserRole):
        user_uid (int):
        username (str):
        email (Union[Unset, str]):
        timezone (Union[Unset, str]):
    """

    default_view: UserView
    is_active: bool
    is_locked: bool
    role: UserRole
    user_uid: int
    username: str
    email: Union[Unset, str] = UNSET
    timezone: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default_view = self.default_view.value
        is_active = self.is_active
        is_locked = self.is_locked
        role = self.role.value
        user_uid = self.user_uid
        username = self.username
        email = self.email
        timezone = self.timezone

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "default_view": default_view,
                "is_active": is_active,
                "is_locked": is_locked,
                "role": role,
                "user_uid": user_uid,
                "username": username,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if timezone is not UNSET:
            field_dict["timezone"] = timezone

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        default_view = UserView(d.pop("default_view"))

        is_active = d.pop("is_active")

        is_locked = d.pop("is_locked")

        role = UserRole(d.pop("role"))

        user_uid = d.pop("user_uid")

        username = d.pop("username")

        _email = d.pop("email", UNSET)
        email = UNSET if _email is None else _email

        _timezone = d.pop("timezone", UNSET)
        timezone = UNSET if _timezone is None else _timezone

        obj = cls(
            default_view=default_view,
            is_active=is_active,
            is_locked=is_locked,
            role=role,
            user_uid=user_uid,
            username=username,
            email=email,
            timezone=timezone,
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
