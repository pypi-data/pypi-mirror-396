from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="NotebookState")


@attrs.define
class NotebookState:
    """
    Attributes:
        dir_path (str):
        enabled (bool):
        notebook_path (str):
    """

    dir_path: str
    enabled: bool
    notebook_path: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dir_path = self.dir_path
        enabled = self.enabled
        notebook_path = self.notebook_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dir_path": dir_path,
                "enabled": enabled,
                "notebook_path": notebook_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dir_path = d.pop("dir_path")

        enabled = d.pop("enabled")

        notebook_path = d.pop("notebook_path")

        obj = cls(
            dir_path=dir_path,
            enabled=enabled,
            notebook_path=notebook_path,
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
