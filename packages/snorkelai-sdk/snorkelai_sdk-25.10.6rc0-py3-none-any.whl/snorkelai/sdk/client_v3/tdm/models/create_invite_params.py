import datetime
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
from dateutil.parser import isoparse

from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateInviteParams")


@attrs.define
class CreateInviteParams:
    """
    Attributes:
        expiration (datetime.datetime):
        max_users_allowed (int):
        role (Union[Unset, UserRole]):
        roles (Union[Unset, List[int]]):
    """

    expiration: datetime.datetime
    max_users_allowed: int
    role: Union[Unset, UserRole] = UNSET
    roles: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        expiration = self.expiration.isoformat()
        max_users_allowed = self.max_users_allowed
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
                "expiration": expiration,
                "max_users_allowed": max_users_allowed,
            }
        )
        if role is not UNSET:
            field_dict["role"] = role
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        expiration = isoparse(d.pop("expiration"))

        max_users_allowed = d.pop("max_users_allowed")

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
            expiration=expiration,
            max_users_allowed=max_users_allowed,
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
