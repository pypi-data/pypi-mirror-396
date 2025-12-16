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

T = TypeVar("T", bound="CreateNodeResponse")


@attrs.define
class CreateNodeResponse:
    """
    Attributes:
        node_uid (int):
        op_version_uid (Union[Unset, int]):
    """

    node_uid: int
    op_version_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        node_uid = self.node_uid
        op_version_uid = self.op_version_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_uid": node_uid,
            }
        )
        if op_version_uid is not UNSET:
            field_dict["op_version_uid"] = op_version_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        node_uid = d.pop("node_uid")

        _op_version_uid = d.pop("op_version_uid", UNSET)
        op_version_uid = UNSET if _op_version_uid is None else _op_version_uid

        obj = cls(
            node_uid=node_uid,
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
