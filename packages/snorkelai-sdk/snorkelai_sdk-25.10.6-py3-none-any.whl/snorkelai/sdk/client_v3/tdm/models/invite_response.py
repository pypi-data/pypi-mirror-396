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

from ..models.user_role import UserRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.role import Role  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="InviteResponse")


@attrs.define
class InviteResponse:
    """
    Attributes:
        created_at (datetime.datetime):
        expiration (datetime.datetime):
        invite_link (str):
        max_users_allowed (int):
        role (UserRole):
        updated_at (datetime.datetime):
        users_accepted (int):
        manually_expired_at (Union[Unset, datetime.datetime]):
        roles (Union[Unset, List['Role']]):
    """

    created_at: datetime.datetime
    expiration: datetime.datetime
    invite_link: str
    max_users_allowed: int
    role: UserRole
    updated_at: datetime.datetime
    users_accepted: int
    manually_expired_at: Union[Unset, datetime.datetime] = UNSET
    roles: Union[Unset, List["Role"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.role import Role  # noqa: F401
        # fmt: on
        created_at = self.created_at.isoformat()
        expiration = self.expiration.isoformat()
        invite_link = self.invite_link
        max_users_allowed = self.max_users_allowed
        role = self.role.value
        updated_at = self.updated_at.isoformat()
        users_accepted = self.users_accepted
        manually_expired_at: Union[Unset, str] = UNSET
        if not isinstance(self.manually_expired_at, Unset):
            manually_expired_at = self.manually_expired_at.isoformat()
        roles: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()
                roles.append(roles_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "expiration": expiration,
                "invite_link": invite_link,
                "max_users_allowed": max_users_allowed,
                "role": role,
                "updated_at": updated_at,
                "users_accepted": users_accepted,
            }
        )
        if manually_expired_at is not UNSET:
            field_dict["manually_expired_at"] = manually_expired_at
        if roles is not UNSET:
            field_dict["roles"] = roles

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.role import Role  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        expiration = isoparse(d.pop("expiration"))

        invite_link = d.pop("invite_link")

        max_users_allowed = d.pop("max_users_allowed")

        role = UserRole(d.pop("role"))

        updated_at = isoparse(d.pop("updated_at"))

        users_accepted = d.pop("users_accepted")

        _manually_expired_at = d.pop("manually_expired_at", UNSET)
        _manually_expired_at = (
            UNSET if _manually_expired_at is None else _manually_expired_at
        )
        manually_expired_at: Union[Unset, datetime.datetime]
        if isinstance(_manually_expired_at, Unset):
            manually_expired_at = UNSET
        else:
            manually_expired_at = isoparse(_manually_expired_at)

        _roles = d.pop("roles", UNSET)
        roles = []
        _roles = UNSET if _roles is None else _roles
        for roles_item_data in _roles or []:
            roles_item = Role.from_dict(roles_item_data)

            roles.append(roles_item)

        obj = cls(
            created_at=created_at,
            expiration=expiration,
            invite_link=invite_link,
            max_users_allowed=max_users_allowed,
            role=role,
            updated_at=updated_at,
            users_accepted=users_accepted,
            manually_expired_at=manually_expired_at,
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
