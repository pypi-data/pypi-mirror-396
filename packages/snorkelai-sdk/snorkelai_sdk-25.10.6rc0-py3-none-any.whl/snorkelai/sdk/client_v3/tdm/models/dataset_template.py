from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetTemplate")


@attrs.define
class DatasetTemplate:
    """Base class for dataset templates.

    Attributes:
        template_id (str):
        ops (Union[Unset, List[str]]):
    """

    template_id: str
    ops: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        template_id = self.template_id
        ops: Union[Unset, List[str]] = UNSET
        if not isinstance(self.ops, Unset):
            ops = self.ops

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template_id": template_id,
            }
        )
        if ops is not UNSET:
            field_dict["ops"] = ops

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        template_id = d.pop("template_id")

        _ops = d.pop("ops", UNSET)
        ops = cast(List[str], UNSET if _ops is None else _ops)

        obj = cls(
            template_id=template_id,
            ops=ops,
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
