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
    from ..models.data_loader_config_rename_columns import (
        DataLoaderConfigRenameColumns,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DataLoaderConfig")


@attrs.define
class DataLoaderConfig:
    """
    Attributes:
        raw_columns (Union[Unset, List[str]]):
        rename_columns (Union[Unset, DataLoaderConfigRenameColumns]):
        suffix (Union[Unset, str]):  Default: ''.
    """

    raw_columns: Union[Unset, List[str]] = UNSET
    rename_columns: Union[Unset, "DataLoaderConfigRenameColumns"] = UNSET
    suffix: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_loader_config_rename_columns import (
            DataLoaderConfigRenameColumns,  # noqa: F401
        )
        # fmt: on
        raw_columns: Union[Unset, List[str]] = UNSET
        if not isinstance(self.raw_columns, Unset):
            raw_columns = self.raw_columns

        rename_columns: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rename_columns, Unset):
            rename_columns = self.rename_columns.to_dict()
        suffix = self.suffix

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if raw_columns is not UNSET:
            field_dict["raw_columns"] = raw_columns
        if rename_columns is not UNSET:
            field_dict["rename_columns"] = rename_columns
        if suffix is not UNSET:
            field_dict["suffix"] = suffix

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_loader_config_rename_columns import (
            DataLoaderConfigRenameColumns,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _raw_columns = d.pop("raw_columns", UNSET)
        raw_columns = cast(List[str], UNSET if _raw_columns is None else _raw_columns)

        _rename_columns = d.pop("rename_columns", UNSET)
        _rename_columns = UNSET if _rename_columns is None else _rename_columns
        rename_columns: Union[Unset, DataLoaderConfigRenameColumns]
        if isinstance(_rename_columns, Unset):
            rename_columns = UNSET
        else:
            rename_columns = DataLoaderConfigRenameColumns.from_dict(_rename_columns)

        _suffix = d.pop("suffix", UNSET)
        suffix = UNSET if _suffix is None else _suffix

        obj = cls(
            raw_columns=raw_columns,
            rename_columns=rename_columns,
            suffix=suffix,
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
