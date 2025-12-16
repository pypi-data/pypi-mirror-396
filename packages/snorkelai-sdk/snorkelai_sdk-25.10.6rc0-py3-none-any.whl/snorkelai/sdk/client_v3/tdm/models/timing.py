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
    from ..models.timing_sub_timings import TimingSubTimings  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Timing")


@attrs.define
class Timing:
    """
    Attributes:
        max_rss_mb (Union[Unset, int]):
        sub_timings (Union[Unset, TimingSubTimings]):
        total_ms (Union[Unset, int]):
    """

    max_rss_mb: Union[Unset, int] = UNSET
    sub_timings: Union[Unset, "TimingSubTimings"] = UNSET
    total_ms: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.timing_sub_timings import TimingSubTimings  # noqa: F401
        # fmt: on
        max_rss_mb = self.max_rss_mb
        sub_timings: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.sub_timings, Unset):
            sub_timings = self.sub_timings.to_dict()
        total_ms = self.total_ms

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_rss_mb is not UNSET:
            field_dict["max_rss_mb"] = max_rss_mb
        if sub_timings is not UNSET:
            field_dict["sub_timings"] = sub_timings
        if total_ms is not UNSET:
            field_dict["total_ms"] = total_ms

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.timing_sub_timings import TimingSubTimings  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _max_rss_mb = d.pop("max_rss_mb", UNSET)
        max_rss_mb = UNSET if _max_rss_mb is None else _max_rss_mb

        _sub_timings = d.pop("sub_timings", UNSET)
        _sub_timings = UNSET if _sub_timings is None else _sub_timings
        sub_timings: Union[Unset, TimingSubTimings]
        if isinstance(_sub_timings, Unset):
            sub_timings = UNSET
        else:
            sub_timings = TimingSubTimings.from_dict(_sub_timings)

        _total_ms = d.pop("total_ms", UNSET)
        total_ms = UNSET if _total_ms is None else _total_ms

        obj = cls(
            max_rss_mb=max_rss_mb,
            sub_timings=sub_timings,
            total_ms=total_ms,
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
