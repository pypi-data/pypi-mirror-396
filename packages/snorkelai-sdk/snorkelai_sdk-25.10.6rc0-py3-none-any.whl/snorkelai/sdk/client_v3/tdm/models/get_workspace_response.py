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
    from ..models.get_workspace_response_user_info_mapping import (
        GetWorkspaceResponseUserInfoMapping,  # noqa: F401
    )
    from ..models.workspace import Workspace  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetWorkspaceResponse")


@attrs.define
class GetWorkspaceResponse:
    """
    Attributes:
        workspace (Workspace):
        user_info_mapping (Union[Unset, GetWorkspaceResponseUserInfoMapping]):
    """

    workspace: "Workspace"
    user_info_mapping: Union[Unset, "GetWorkspaceResponseUserInfoMapping"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.get_workspace_response_user_info_mapping import (
            GetWorkspaceResponseUserInfoMapping,  # noqa: F401
        )
        from ..models.workspace import Workspace  # noqa: F401
        # fmt: on
        workspace = self.workspace.to_dict()
        user_info_mapping: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_info_mapping, Unset):
            user_info_mapping = self.user_info_mapping.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace": workspace,
            }
        )
        if user_info_mapping is not UNSET:
            field_dict["user_info_mapping"] = user_info_mapping

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.get_workspace_response_user_info_mapping import (
            GetWorkspaceResponseUserInfoMapping,  # noqa: F401
        )
        from ..models.workspace import Workspace  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        workspace = Workspace.from_dict(d.pop("workspace"))

        _user_info_mapping = d.pop("user_info_mapping", UNSET)
        _user_info_mapping = UNSET if _user_info_mapping is None else _user_info_mapping
        user_info_mapping: Union[Unset, GetWorkspaceResponseUserInfoMapping]
        if isinstance(_user_info_mapping, Unset):
            user_info_mapping = UNSET
        else:
            user_info_mapping = GetWorkspaceResponseUserInfoMapping.from_dict(
                _user_info_mapping
            )

        obj = cls(
            workspace=workspace,
            user_info_mapping=user_info_mapping,
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
