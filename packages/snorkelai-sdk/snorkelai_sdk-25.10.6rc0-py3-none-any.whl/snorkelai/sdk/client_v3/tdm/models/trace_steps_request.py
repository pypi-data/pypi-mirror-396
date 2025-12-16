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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.trace_index import TraceIndex  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="TraceStepsRequest")


@attrs.define
class TraceStepsRequest:
    """
    Attributes:
        trace_index (TraceIndex):
        criteria_uid (Union[Unset, int]):
        filter_config_str (Union[Unset, str]):
    """

    trace_index: "TraceIndex"
    criteria_uid: Union[Unset, int] = UNSET
    filter_config_str: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.trace_index import TraceIndex  # noqa: F401
        # fmt: on
        trace_index = self.trace_index.to_dict()
        criteria_uid = self.criteria_uid
        filter_config_str = self.filter_config_str

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "trace_index": trace_index,
            }
        )
        if criteria_uid is not UNSET:
            field_dict["criteria_uid"] = criteria_uid
        if filter_config_str is not UNSET:
            field_dict["filter_config_str"] = filter_config_str

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.trace_index import TraceIndex  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        trace_index = TraceIndex.from_dict(d.pop("trace_index"))

        _criteria_uid = d.pop("criteria_uid", UNSET)
        criteria_uid = UNSET if _criteria_uid is None else _criteria_uid

        _filter_config_str = d.pop("filter_config_str", UNSET)
        filter_config_str = UNSET if _filter_config_str is None else _filter_config_str

        obj = cls(
            trace_index=trace_index,
            criteria_uid=criteria_uid,
            filter_config_str=filter_config_str,
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
