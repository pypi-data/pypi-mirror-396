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
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureAccessRole")


@attrs.define
class FeatureAccessRole:
    """
    Attributes:
        mapping_uid (int):
        user_roles (List[UserRole]):
        workspace_uid (Union[Unset, int]):
    """

    mapping_uid: int
    user_roles: List[UserRole]
    workspace_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        mapping_uid = self.mapping_uid
        user_roles = []
        for user_roles_item_data in self.user_roles:
            user_roles_item = user_roles_item_data.value
            user_roles.append(user_roles_item)

        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mapping_uid": mapping_uid,
                "user_roles": user_roles,
            }
        )
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        mapping_uid = d.pop("mapping_uid")

        user_roles = []
        _user_roles = d.pop("user_roles")
        for user_roles_item_data in _user_roles:
            user_roles_item = UserRole(user_roles_item_data)

            user_roles.append(user_roles_item)

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            mapping_uid=mapping_uid,
            user_roles=user_roles,
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
