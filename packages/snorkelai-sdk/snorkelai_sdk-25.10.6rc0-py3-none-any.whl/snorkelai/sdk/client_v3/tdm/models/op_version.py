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
    from ..models.op_version_op_config import OpVersionOpConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="OpVersion")


@attrs.define
class OpVersion:
    """Class for saving, deleting, and manipulating versions of Nodes,
    e.g. different model configs hyperparameters are stored as op-versions,
    until the "best" model is committed to the node

        Attributes:
            node_uid (int):
            op_config (OpVersionOpConfig):
            op_type (str):
            created_at (Union[Unset, datetime.datetime]):
            name (Union[Unset, str]):
            op_version_uid (Union[Unset, int]):
    """

    node_uid: int
    op_config: "OpVersionOpConfig"
    op_type: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    name: Union[Unset, str] = UNSET
    op_version_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.op_version_op_config import OpVersionOpConfig  # noqa: F401
        # fmt: on
        node_uid = self.node_uid
        op_config = self.op_config.to_dict()
        op_type = self.op_type
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        name = self.name
        op_version_uid = self.op_version_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_uid": node_uid,
                "op_config": op_config,
                "op_type": op_type,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if name is not UNSET:
            field_dict["name"] = name
        if op_version_uid is not UNSET:
            field_dict["op_version_uid"] = op_version_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.op_version_op_config import OpVersionOpConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        node_uid = d.pop("node_uid")

        op_config = OpVersionOpConfig.from_dict(d.pop("op_config"))

        op_type = d.pop("op_type")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _name = d.pop("name", UNSET)
        name = UNSET if _name is None else _name

        _op_version_uid = d.pop("op_version_uid", UNSET)
        op_version_uid = UNSET if _op_version_uid is None else _op_version_uid

        obj = cls(
            node_uid=node_uid,
            op_config=op_config,
            op_type=op_type,
            created_at=created_at,
            name=name,
            op_version_uid=op_version_uid,
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
