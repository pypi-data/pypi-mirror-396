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
from ..models.data_connector import DataConnector
from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataConnectorRole")


@attrs.define
class DataConnectorRole:
    """
    Attributes:
        data_connector_type (DataConnector):
        permissions (List[CRUDAction]):
        role_uid (int):
        user_roles (List[UserRole]):
        workspace_name (str):
        workspace_uid (Union[Unset, int]):
    """

    data_connector_type: DataConnector
    permissions: List[CRUDAction]
    role_uid: int
    user_roles: List[UserRole]
    workspace_name: str
    workspace_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data_connector_type = self.data_connector_type.value
        permissions = []
        for permissions_item_data in self.permissions:
            permissions_item = permissions_item_data.value
            permissions.append(permissions_item)

        role_uid = self.role_uid
        user_roles = []
        for user_roles_item_data in self.user_roles:
            user_roles_item = user_roles_item_data.value
            user_roles.append(user_roles_item)

        workspace_name = self.workspace_name
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_connector_type": data_connector_type,
                "permissions": permissions,
                "role_uid": role_uid,
                "user_roles": user_roles,
                "workspace_name": workspace_name,
            }
        )
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_connector_type = DataConnector(d.pop("data_connector_type"))

        permissions = []
        _permissions = d.pop("permissions")
        for permissions_item_data in _permissions:
            permissions_item = CRUDAction(permissions_item_data)

            permissions.append(permissions_item)

        role_uid = d.pop("role_uid")

        user_roles = []
        _user_roles = d.pop("user_roles")
        for user_roles_item_data in _user_roles:
            user_roles_item = UserRole(user_roles_item_data)

            user_roles.append(user_roles_item)

        workspace_name = d.pop("workspace_name")

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            data_connector_type=data_connector_type,
            permissions=permissions,
            role_uid=role_uid,
            user_roles=user_roles,
            workspace_name=workspace_name,
            workspace_uid=workspace_uid,
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
