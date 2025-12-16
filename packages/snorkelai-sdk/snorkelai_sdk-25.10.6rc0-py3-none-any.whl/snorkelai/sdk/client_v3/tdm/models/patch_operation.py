from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.op import Op
from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchOperation")


@attrs.define
class PatchOperation:
    """
    Attributes:
        op (Union[Unset, Op]):
        path (Union[Unset, str]): The "path" attribute value is a String containing an attribute path
            describing the target of the operation.
        value (Union[Unset, Any]):
    """

    op: Union[Unset, Op] = UNSET
    path: Union[Unset, str] = UNSET
    value: Union[Unset, Any] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        op: Union[Unset, str] = UNSET
        if not isinstance(self.op, Unset):
            op = self.op.value

        path = self.path
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if op is not UNSET:
            field_dict["op"] = op
        if path is not UNSET:
            field_dict["path"] = path
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _op = d.pop("op", UNSET)
        _op = UNSET if _op is None else _op
        op: Union[Unset, Op]
        if isinstance(_op, Unset):
            op = UNSET
        else:
            op = Op(_op)

        _path = d.pop("path", UNSET)
        path = UNSET if _path is None else _path

        _value = d.pop("value", UNSET)
        value = UNSET if _value is None else _value

        obj = cls(
            op=op,
            path=path,
            value=value,
        )
        return obj
