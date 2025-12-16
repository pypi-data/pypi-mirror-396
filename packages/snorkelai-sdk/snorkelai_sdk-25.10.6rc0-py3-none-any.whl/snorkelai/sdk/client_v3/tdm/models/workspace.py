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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.workspace_config import WorkspaceConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Workspace")


@attrs.define
class Workspace:
    """
    Attributes:
        config (WorkspaceConfig):
        name (str):
        created_at (Union[Unset, datetime.datetime]):
        workspace_uid (Union[Unset, int]):
    """

    config: "WorkspaceConfig"
    name: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    workspace_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.workspace_config import WorkspaceConfig  # noqa: F401
        # fmt: on
        config = self.config.to_dict()
        name = self.name
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "name": name,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.workspace_config import WorkspaceConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        config = WorkspaceConfig.from_dict(d.pop("config"))

        name = d.pop("name")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            config=config,
            name=name,
            created_at=created_at,
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
