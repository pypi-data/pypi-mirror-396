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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.patch_workspace_roles_payload_user_role_mapping import (
        PatchWorkspaceRolesPayloadUserRoleMapping,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PatchWorkspaceRolesPayload")


@attrs.define
class PatchWorkspaceRolesPayload:
    """
    Attributes:
        user_role_mapping (Union[Unset, PatchWorkspaceRolesPayloadUserRoleMapping]):
    """

    user_role_mapping: Union[Unset, "PatchWorkspaceRolesPayloadUserRoleMapping"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.patch_workspace_roles_payload_user_role_mapping import (
            PatchWorkspaceRolesPayloadUserRoleMapping,  # noqa: F401
        )
        # fmt: on
        user_role_mapping: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_role_mapping, Unset):
            user_role_mapping = self.user_role_mapping.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_role_mapping is not UNSET:
            field_dict["user_role_mapping"] = user_role_mapping

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.patch_workspace_roles_payload_user_role_mapping import (
            PatchWorkspaceRolesPayloadUserRoleMapping,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _user_role_mapping = d.pop("user_role_mapping", UNSET)
        _user_role_mapping = UNSET if _user_role_mapping is None else _user_role_mapping
        user_role_mapping: Union[Unset, PatchWorkspaceRolesPayloadUserRoleMapping]
        if isinstance(_user_role_mapping, Unset):
            user_role_mapping = UNSET
        else:
            user_role_mapping = PatchWorkspaceRolesPayloadUserRoleMapping.from_dict(
                _user_role_mapping
            )

        obj = cls(
            user_role_mapping=user_role_mapping,
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
