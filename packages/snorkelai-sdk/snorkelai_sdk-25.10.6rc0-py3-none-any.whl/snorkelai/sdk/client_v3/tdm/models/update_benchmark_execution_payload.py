from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.benchmark_execution_state import BenchmarkExecutionState
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateBenchmarkExecutionPayload")


@attrs.define
class UpdateBenchmarkExecutionPayload:
    """
    Attributes:
        state (Union[Unset, BenchmarkExecutionState]):
    """

    state: Union[Unset, BenchmarkExecutionState] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _state = d.pop("state", UNSET)
        _state = UNSET if _state is None else _state
        state: Union[Unset, BenchmarkExecutionState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = BenchmarkExecutionState(_state)

        obj = cls(
            state=state,
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
