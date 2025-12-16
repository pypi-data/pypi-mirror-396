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

T = TypeVar("T", bound="LatestErrorAnalysisRunResponse")


@attrs.define
class LatestErrorAnalysisRunResponse:
    """Response payload for getting the latest error analysis run.

    Attributes:
        error_analysis_run_id (Union[Unset, int]):
    """

    error_analysis_run_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        error_analysis_run_id = self.error_analysis_run_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error_analysis_run_id is not UNSET:
            field_dict["error_analysis_run_id"] = error_analysis_run_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _error_analysis_run_id = d.pop("error_analysis_run_id", UNSET)
        error_analysis_run_id = (
            UNSET if _error_analysis_run_id is None else _error_analysis_run_id
        )

        obj = cls(
            error_analysis_run_id=error_analysis_run_id,
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
