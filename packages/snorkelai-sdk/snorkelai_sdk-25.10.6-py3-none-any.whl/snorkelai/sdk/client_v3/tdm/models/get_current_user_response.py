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

T = TypeVar("T", bound="GetCurrentUserResponse")


@attrs.define
class GetCurrentUserResponse:
    """
    Attributes:
        default_view (UserView):
        user_roles (List[UserRole]):
        user_uid (int):
        username (str):
        email (Union[Unset, str]):
        role (Union[Unset, UserRole]):
        timezone (Union[Unset, str]):
    """

    default_view: UserView
    user_roles: List[UserRole]
    user_uid: int
    username: str
    email: Union[Unset, str] = UNSET
    role: Union[Unset, UserRole] = UNSET
    timezone: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        default_view = self.default_view.value
        user_roles = []
        for user_roles_item_data in self.user_roles:
            user_roles_item = user_roles_item_data.value
            user_roles.append(user_roles_item)

        user_uid = self.user_uid
        username = self.username
        email = self.email
        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        timezone = self.timezone

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "default_view": default_view,
                "user_roles": user_roles,
                "user_uid": user_uid,
                "username": username,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if role is not UNSET:
            field_dict["role"] = role
        if timezone is not UNSET:
            field_dict["timezone"] = timezone

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        default_view = UserView(d.pop("default_view"))

        user_roles = []
        _user_roles = d.pop("user_roles")
        for user_roles_item_data in _user_roles:
            user_roles_item = UserRole(user_roles_item_data)

            user_roles.append(user_roles_item)

        user_uid = d.pop("user_uid")

        username = d.pop("username")

        _email = d.pop("email", UNSET)
        email = UNSET if _email is None else _email

        _role = d.pop("role", UNSET)
        _role = UNSET if _role is None else _role
        role: Union[Unset, UserRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = UserRole(_role)

        _timezone = d.pop("timezone", UNSET)
        timezone = UNSET if _timezone is None else _timezone

        obj = cls(
            default_view=default_view,
            user_roles=user_roles,
            user_uid=user_uid,
            username=username,
            email=email,
            role=role,
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
