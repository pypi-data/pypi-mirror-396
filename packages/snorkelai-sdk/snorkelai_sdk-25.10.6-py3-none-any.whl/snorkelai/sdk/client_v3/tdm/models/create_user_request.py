from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUserRequest")


@attrs.define
class CreateUserRequest:
    """
    Attributes:
        password (str):
        username (str):
        default_view (Union[Unset, str]):
        email (Union[Unset, str]):
        invite_link (Union[Unset, str]):
        role (Union[Unset, UserRole]):
        roles (Union[Unset, List[int]]):
    """

    password: str
    username: str
    default_view: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    invite_link: Union[Unset, str] = UNSET
    role: Union[Unset, UserRole] = UNSET
    roles: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        password = self.password
        username = self.username
        default_view = self.default_view
        email = self.email
        invite_link = self.invite_link
        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        roles: Union[Unset, List[int]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "password": password,
                "username": username,
            }
        )
        if default_view is not UNSET:
            field_dict["default_view"] = default_view
        if email is not UNSET:
            field_dict["email"] = email
        if invite_link is not UNSET:
            field_dict["invite_link"] = invite_link
        if role is not UNSET:
            field_dict["role"] = role
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        password = d.pop("password")

        username = d.pop("username")

        _default_view = d.pop("default_view", UNSET)
        default_view = UNSET if _default_view is None else _default_view

        _email = d.pop("email", UNSET)
        email = UNSET if _email is None else _email

        _invite_link = d.pop("invite_link", UNSET)
        invite_link = UNSET if _invite_link is None else _invite_link

        _role = d.pop("role", UNSET)
        _role = UNSET if _role is None else _role
        role: Union[Unset, UserRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = UserRole(_role)

        _roles = d.pop("roles", UNSET)
        roles = cast(List[int], UNSET if _roles is None else _roles)

        obj = cls(
            password=password,
            username=username,
            default_view=default_view,
            email=email,
            invite_link=invite_link,
            role=role,
            roles=roles,
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
