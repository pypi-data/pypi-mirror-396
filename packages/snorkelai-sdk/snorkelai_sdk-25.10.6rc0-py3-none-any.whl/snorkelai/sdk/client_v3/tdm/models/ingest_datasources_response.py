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
    from ..models.ingest_single_datasource_response import (
        IngestSingleDatasourceResponse,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="IngestDatasourcesResponse")


@attrs.define
class IngestDatasourcesResponse:
    """Response for ingesting multiple datasources at once.

    Attributes:
        results_by_source (List['IngestSingleDatasourceResponse']):
    """

    results_by_source: List["IngestSingleDatasourceResponse"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ingest_single_datasource_response import (
            IngestSingleDatasourceResponse,  # noqa: F401
        )
        # fmt: on
        results_by_source = []
        for results_by_source_item_data in self.results_by_source:
            results_by_source_item = results_by_source_item_data.to_dict()
            results_by_source.append(results_by_source_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results_by_source": results_by_source,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ingest_single_datasource_response import (
            IngestSingleDatasourceResponse,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        results_by_source = []
        _results_by_source = d.pop("results_by_source")
        for results_by_source_item_data in _results_by_source:
            results_by_source_item = IngestSingleDatasourceResponse.from_dict(
                results_by_source_item_data
            )

            results_by_source.append(results_by_source_item)

        obj = cls(
            results_by_source=results_by_source,
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
