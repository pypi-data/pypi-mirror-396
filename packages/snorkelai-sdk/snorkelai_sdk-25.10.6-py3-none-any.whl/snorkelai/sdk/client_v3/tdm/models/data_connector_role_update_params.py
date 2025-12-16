from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.crud_action import CRUDAction
from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataConnectorRoleUpdateParams")


@attrs.define
class DataConnectorRoleUpdateParams:
    """
    Attributes:
        new_permissions (List[CRUDAction]):
        new_user_roles (List[UserRole]):
        new_workspace_uid (Union[Unset, int]):
    """

    new_permissions: List[CRUDAction]
    new_user_roles: List[UserRole]
    new_workspace_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_permissions = []
        for new_permissions_item_data in self.new_permissions:
            new_permissions_item = new_permissions_item_data.value
            new_permissions.append(new_permissions_item)

        new_user_roles = []
        for new_user_roles_item_data in self.new_user_roles:
            new_user_roles_item = new_user_roles_item_data.value
            new_user_roles.append(new_user_roles_item)

        new_workspace_uid = self.new_workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_permissions": new_permissions,
                "new_user_roles": new_user_roles,
            }
        )
        if new_workspace_uid is not UNSET:
            field_dict["new_workspace_uid"] = new_workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        new_permissions = []
        _new_permissions = d.pop("new_permissions")
        for new_permissions_item_data in _new_permissions:
            new_permissions_item = CRUDAction(new_permissions_item_data)

            new_permissions.append(new_permissions_item)

        new_user_roles = []
        _new_user_roles = d.pop("new_user_roles")
        for new_user_roles_item_data in _new_user_roles:
            new_user_roles_item = UserRole(new_user_roles_item_data)

            new_user_roles.append(new_user_roles_item)

        _new_workspace_uid = d.pop("new_workspace_uid", UNSET)
        new_workspace_uid = UNSET if _new_workspace_uid is None else _new_workspace_uid

        obj = cls(
            new_permissions=new_permissions,
            new_user_roles=new_user_roles,
            new_workspace_uid=new_workspace_uid,
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
