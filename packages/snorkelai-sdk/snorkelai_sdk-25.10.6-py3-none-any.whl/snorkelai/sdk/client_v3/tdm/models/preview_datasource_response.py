from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.preview_datasource_response_sample_rows_item import (
        PreviewDatasourceResponseSampleRowsItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PreviewDatasourceResponse")


@attrs.define
class PreviewDatasourceResponse:
    """Response for peeking at sample data from a datasource.

    Attributes:
        columns (List[str]):
        sample_rows (List['PreviewDatasourceResponseSampleRowsItem']):
    """

    columns: List[str]
    sample_rows: List["PreviewDatasourceResponseSampleRowsItem"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.preview_datasource_response_sample_rows_item import (
            PreviewDatasourceResponseSampleRowsItem,  # noqa: F401
        )
        # fmt: on
        columns = self.columns

        sample_rows = []
        for sample_rows_item_data in self.sample_rows:
            sample_rows_item = sample_rows_item_data.to_dict()
            sample_rows.append(sample_rows_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "columns": columns,
                "sample_rows": sample_rows,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.preview_datasource_response_sample_rows_item import (
            PreviewDatasourceResponseSampleRowsItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        columns = cast(List[str], d.pop("columns"))

        sample_rows = []
        _sample_rows = d.pop("sample_rows")
        for sample_rows_item_data in _sample_rows:
            sample_rows_item = PreviewDatasourceResponseSampleRowsItem.from_dict(
                sample_rows_item_data
            )

            sample_rows.append(sample_rows_item)

        obj = cls(
            columns=columns,
            sample_rows=sample_rows,
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
