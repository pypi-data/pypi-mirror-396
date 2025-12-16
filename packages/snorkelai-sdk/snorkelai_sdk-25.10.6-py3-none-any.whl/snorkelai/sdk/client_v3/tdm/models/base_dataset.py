from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="BaseDataset")


@attrs.define
class BaseDataset:
    """
    Attributes:
        name (str):
        workspace_uid (Union[Unset, int]):  Default: 1.
    """

    name: str
    workspace_uid: Union[Unset, int] = 1
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            name=name,
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
