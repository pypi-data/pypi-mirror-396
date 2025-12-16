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
    from ..models.trace_steps import TraceSteps  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="TraceStepsResponse")


@attrs.define
class TraceStepsResponse:
    """
    Attributes:
        count (int):
        root_step (TraceSteps):
        trace (str):
    """

    count: int
    root_step: "TraceSteps"
    trace: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.trace_steps import TraceSteps  # noqa: F401
        # fmt: on
        count = self.count
        root_step = self.root_step.to_dict()
        trace = self.trace

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "root_step": root_step,
                "trace": trace,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.trace_steps import TraceSteps  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        count = d.pop("count")

        root_step = TraceSteps.from_dict(d.pop("root_step"))

        trace = d.pop("trace")

        obj = cls(
            count=count,
            root_step=root_step,
            trace=trace,
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
