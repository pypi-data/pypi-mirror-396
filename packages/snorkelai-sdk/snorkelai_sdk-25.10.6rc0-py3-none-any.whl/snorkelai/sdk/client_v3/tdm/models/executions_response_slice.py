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
    from ..models.executions_response_slice_count import (
        ExecutionsResponseSliceCount,  # noqa: F401
    )
    from ..models.executions_response_slice_coverage import (
        ExecutionsResponseSliceCoverage,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ExecutionsResponseSlice")


@attrs.define
class ExecutionsResponseSlice:
    """
    Attributes:
        display_name (str):
        id (str):
        reserved_slice_type (str):
        count (Union[Unset, ExecutionsResponseSliceCount]):
        coverage (Union[Unset, ExecutionsResponseSliceCoverage]):
    """

    display_name: str
    id: str
    reserved_slice_type: str
    count: Union[Unset, "ExecutionsResponseSliceCount"] = UNSET
    coverage: Union[Unset, "ExecutionsResponseSliceCoverage"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.executions_response_slice_count import (
            ExecutionsResponseSliceCount,  # noqa: F401
        )
        from ..models.executions_response_slice_coverage import (
            ExecutionsResponseSliceCoverage,  # noqa: F401
        )
        # fmt: on
        display_name = self.display_name
        id = self.id
        reserved_slice_type = self.reserved_slice_type
        count: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.count, Unset):
            count = self.count.to_dict()
        coverage: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.coverage, Unset):
            coverage = self.coverage.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "id": id,
                "reserved_slice_type": reserved_slice_type,
            }
        )
        if count is not UNSET:
            field_dict["count"] = count
        if coverage is not UNSET:
            field_dict["coverage"] = coverage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.executions_response_slice_count import (
            ExecutionsResponseSliceCount,  # noqa: F401
        )
        from ..models.executions_response_slice_coverage import (
            ExecutionsResponseSliceCoverage,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        display_name = d.pop("display_name")

        id = d.pop("id")

        reserved_slice_type = d.pop("reserved_slice_type")

        _count = d.pop("count", UNSET)
        _count = UNSET if _count is None else _count
        count: Union[Unset, ExecutionsResponseSliceCount]
        if isinstance(_count, Unset):
            count = UNSET
        else:
            count = ExecutionsResponseSliceCount.from_dict(_count)

        _coverage = d.pop("coverage", UNSET)
        _coverage = UNSET if _coverage is None else _coverage
        coverage: Union[Unset, ExecutionsResponseSliceCoverage]
        if isinstance(_coverage, Unset):
            coverage = UNSET
        else:
            coverage = ExecutionsResponseSliceCoverage.from_dict(_coverage)

        obj = cls(
            display_name=display_name,
            id=id,
            reserved_slice_type=reserved_slice_type,
            count=count,
            coverage=coverage,
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
