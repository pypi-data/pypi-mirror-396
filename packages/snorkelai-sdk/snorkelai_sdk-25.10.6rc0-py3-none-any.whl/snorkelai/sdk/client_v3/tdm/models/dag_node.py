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

T = TypeVar("T", bound="DAGNode")


@attrs.define
class DAGNode:
    """
    Attributes:
        input_ids (List[int]):
        is_output (Union[Unset, bool]):  Default: False.
    """

    input_ids: List[int]
    is_output: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        input_ids = self.input_ids

        is_output = self.is_output

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_ids": input_ids,
            }
        )
        if is_output is not UNSET:
            field_dict["is_output"] = is_output

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        input_ids = cast(List[int], d.pop("input_ids"))

        _is_output = d.pop("is_output", UNSET)
        is_output = UNSET if _is_output is None else _is_output

        obj = cls(
            input_ids=input_ids,
            is_output=is_output,
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
