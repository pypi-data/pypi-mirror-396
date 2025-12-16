from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.workspace import Workspace  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ListWorkspaceResponse")


@attrs.define
class ListWorkspaceResponse:
    """
    Attributes:
        workspaces (List['Workspace']):
    """

    workspaces: List["Workspace"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.workspace import Workspace  # noqa: F401
        # fmt: on
        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspaces": workspaces,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.workspace import Workspace  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = Workspace.from_dict(workspaces_item_data)

            workspaces.append(workspaces_item)

        obj = cls(
            workspaces=workspaces,
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
