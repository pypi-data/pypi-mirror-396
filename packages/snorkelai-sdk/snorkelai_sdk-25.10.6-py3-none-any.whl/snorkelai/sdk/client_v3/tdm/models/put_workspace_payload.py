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
    from ..models.workspace_config import WorkspaceConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PutWorkspacePayload")


@attrs.define
class PutWorkspacePayload:
    """
    Attributes:
        config (WorkspaceConfig):
        name (str):
    """

    config: "WorkspaceConfig"
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.workspace_config import WorkspaceConfig  # noqa: F401
        # fmt: on
        config = self.config.to_dict()
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.workspace_config import WorkspaceConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        config = WorkspaceConfig.from_dict(d.pop("config"))

        name = d.pop("name")

        obj = cls(
            config=config,
            name=name,
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
