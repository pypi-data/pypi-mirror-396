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
    from ..models.analysis_params import AnalysisParams  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnalyzeDatasourcesRequest")


@attrs.define
class AnalyzeDatasourcesRequest:
    """Request model for analyzing one or more data sources.

    Attributes:
        datasources (List['AnalysisParams']):
    """

    datasources: List["AnalysisParams"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.analysis_params import AnalysisParams  # noqa: F401
        # fmt: on
        datasources = []
        for datasources_item_data in self.datasources:
            datasources_item = datasources_item_data.to_dict()
            datasources.append(datasources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasources": datasources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.analysis_params import AnalysisParams  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        datasources = []
        _datasources = d.pop("datasources")
        for datasources_item_data in _datasources:
            datasources_item = AnalysisParams.from_dict(datasources_item_data)

            datasources.append(datasources_item)

        obj = cls(
            datasources=datasources,
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
