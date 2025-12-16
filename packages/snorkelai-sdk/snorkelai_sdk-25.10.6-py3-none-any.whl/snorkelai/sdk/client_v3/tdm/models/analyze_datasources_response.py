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
    from ..models.single_source_analysis_result import (
        SingleSourceAnalysisResult,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AnalyzeDatasourcesResponse")


@attrs.define
class AnalyzeDatasourcesResponse:
    """Response containing analysis results for multiple data sources.

    Attributes:
        results (List['SingleSourceAnalysisResult']):
    """

    results: List["SingleSourceAnalysisResult"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.single_source_analysis_result import (
            SingleSourceAnalysisResult,  # noqa: F401
        )
        # fmt: on
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.single_source_analysis_result import (
            SingleSourceAnalysisResult,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = SingleSourceAnalysisResult.from_dict(results_item_data)

            results.append(results_item)

        obj = cls(
            results=results,
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
