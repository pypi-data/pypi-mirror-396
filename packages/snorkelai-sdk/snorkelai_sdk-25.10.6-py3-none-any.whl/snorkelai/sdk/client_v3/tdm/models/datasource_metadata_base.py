from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.datasource_metadata_base_column_types import (
        DatasourceMetadataBaseColumnTypes,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DatasourceMetadataBase")


@attrs.define
class DatasourceMetadataBase:
    """
    Attributes:
        column_types (Union[Unset, DatasourceMetadataBaseColumnTypes]):
        columns (Union[Unset, List[str]]):
        migration_schema_version (Union[Unset, int]):
        n_datapoints (Union[Unset, int]):
        n_docs (Union[Unset, int]):
        size_bytes (Union[Unset, int]):
    """

    column_types: Union[Unset, "DatasourceMetadataBaseColumnTypes"] = UNSET
    columns: Union[Unset, List[str]] = UNSET
    migration_schema_version: Union[Unset, int] = UNSET
    n_datapoints: Union[Unset, int] = UNSET
    n_docs: Union[Unset, int] = UNSET
    size_bytes: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.datasource_metadata_base_column_types import (
            DatasourceMetadataBaseColumnTypes,  # noqa: F401
        )
        # fmt: on
        column_types: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.column_types, Unset):
            column_types = self.column_types.to_dict()
        columns: Union[Unset, List[str]] = UNSET
        if not isinstance(self.columns, Unset):
            columns = self.columns

        migration_schema_version = self.migration_schema_version
        n_datapoints = self.n_datapoints
        n_docs = self.n_docs
        size_bytes = self.size_bytes

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if column_types is not UNSET:
            field_dict["column_types"] = column_types
        if columns is not UNSET:
            field_dict["columns"] = columns
        if migration_schema_version is not UNSET:
            field_dict["migration_schema_version"] = migration_schema_version
        if n_datapoints is not UNSET:
            field_dict["n_datapoints"] = n_datapoints
        if n_docs is not UNSET:
            field_dict["n_docs"] = n_docs
        if size_bytes is not UNSET:
            field_dict["size_bytes"] = size_bytes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.datasource_metadata_base_column_types import (
            DatasourceMetadataBaseColumnTypes,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _column_types = d.pop("column_types", UNSET)
        _column_types = UNSET if _column_types is None else _column_types
        column_types: Union[Unset, DatasourceMetadataBaseColumnTypes]
        if isinstance(_column_types, Unset):
            column_types = UNSET
        else:
            column_types = DatasourceMetadataBaseColumnTypes.from_dict(_column_types)

        _columns = d.pop("columns", UNSET)
        columns = cast(List[str], UNSET if _columns is None else _columns)

        _migration_schema_version = d.pop("migration_schema_version", UNSET)
        migration_schema_version = (
            UNSET if _migration_schema_version is None else _migration_schema_version
        )

        _n_datapoints = d.pop("n_datapoints", UNSET)
        n_datapoints = UNSET if _n_datapoints is None else _n_datapoints

        _n_docs = d.pop("n_docs", UNSET)
        n_docs = UNSET if _n_docs is None else _n_docs

        _size_bytes = d.pop("size_bytes", UNSET)
        size_bytes = UNSET if _size_bytes is None else _size_bytes

        obj = cls(
            column_types=column_types,
            columns=columns,
            migration_schema_version=migration_schema_version,
            n_datapoints=n_datapoints,
            n_docs=n_docs,
            size_bytes=size_bytes,
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
