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
    from ..models.datasource_analysis_response_column_map import (
        DatasourceAnalysisResponseColumnMap,  # noqa: F401
    )
    from ..models.datasource_analysis_response_load_configs_item import (
        DatasourceAnalysisResponseLoadConfigsItem,  # noqa: F401
    )
    from ..models.input_warning import InputWarning  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DatasourceAnalysisResponse")


@attrs.define
class DatasourceAnalysisResponse:
    """
    Attributes:
        datestamp (str):
        split (str):
        allow_generate_uid_col (Union[Unset, bool]):  Default: False.
        column_map (Union[Unset, DatasourceAnalysisResponseColumnMap]):
        load_configs (Union[Unset, List['DatasourceAnalysisResponseLoadConfigsItem']]):
        potential_uid_columns (Union[Unset, List[str]]):
        warnings (Union[Unset, List['InputWarning']]):
    """

    datestamp: str
    split: str
    allow_generate_uid_col: Union[Unset, bool] = False
    column_map: Union[Unset, "DatasourceAnalysisResponseColumnMap"] = UNSET
    load_configs: Union[Unset, List["DatasourceAnalysisResponseLoadConfigsItem"]] = (
        UNSET
    )
    potential_uid_columns: Union[Unset, List[str]] = UNSET
    warnings: Union[Unset, List["InputWarning"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.datasource_analysis_response_column_map import (
            DatasourceAnalysisResponseColumnMap,  # noqa: F401
        )
        from ..models.datasource_analysis_response_load_configs_item import (
            DatasourceAnalysisResponseLoadConfigsItem,  # noqa: F401
        )
        from ..models.input_warning import InputWarning  # noqa: F401
        # fmt: on
        datestamp = self.datestamp
        split = self.split
        allow_generate_uid_col = self.allow_generate_uid_col
        column_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.column_map, Unset):
            column_map = self.column_map.to_dict()
        load_configs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.load_configs, Unset):
            load_configs = []
            for load_configs_item_data in self.load_configs:
                load_configs_item = load_configs_item_data.to_dict()
                load_configs.append(load_configs_item)

        potential_uid_columns: Union[Unset, List[str]] = UNSET
        if not isinstance(self.potential_uid_columns, Unset):
            potential_uid_columns = self.potential_uid_columns

        warnings: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = []
            for warnings_item_data in self.warnings:
                warnings_item = warnings_item_data.to_dict()
                warnings.append(warnings_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datestamp": datestamp,
                "split": split,
            }
        )
        if allow_generate_uid_col is not UNSET:
            field_dict["allow_generate_uid_col"] = allow_generate_uid_col
        if column_map is not UNSET:
            field_dict["column_map"] = column_map
        if load_configs is not UNSET:
            field_dict["load_configs"] = load_configs
        if potential_uid_columns is not UNSET:
            field_dict["potential_uid_columns"] = potential_uid_columns
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.datasource_analysis_response_column_map import (
            DatasourceAnalysisResponseColumnMap,  # noqa: F401
        )
        from ..models.datasource_analysis_response_load_configs_item import (
            DatasourceAnalysisResponseLoadConfigsItem,  # noqa: F401
        )
        from ..models.input_warning import InputWarning  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        datestamp = d.pop("datestamp")

        split = d.pop("split")

        _allow_generate_uid_col = d.pop("allow_generate_uid_col", UNSET)
        allow_generate_uid_col = (
            UNSET if _allow_generate_uid_col is None else _allow_generate_uid_col
        )

        _column_map = d.pop("column_map", UNSET)
        _column_map = UNSET if _column_map is None else _column_map
        column_map: Union[Unset, DatasourceAnalysisResponseColumnMap]
        if isinstance(_column_map, Unset):
            column_map = UNSET
        else:
            column_map = DatasourceAnalysisResponseColumnMap.from_dict(_column_map)

        _load_configs = d.pop("load_configs", UNSET)
        load_configs = []
        _load_configs = UNSET if _load_configs is None else _load_configs
        for load_configs_item_data in _load_configs or []:
            load_configs_item = DatasourceAnalysisResponseLoadConfigsItem.from_dict(
                load_configs_item_data
            )

            load_configs.append(load_configs_item)

        _potential_uid_columns = d.pop("potential_uid_columns", UNSET)
        potential_uid_columns = cast(
            List[str],
            UNSET if _potential_uid_columns is None else _potential_uid_columns,
        )

        _warnings = d.pop("warnings", UNSET)
        warnings = []
        _warnings = UNSET if _warnings is None else _warnings
        for warnings_item_data in _warnings or []:
            warnings_item = InputWarning.from_dict(warnings_item_data)

            warnings.append(warnings_item)

        obj = cls(
            datestamp=datestamp,
            split=split,
            allow_generate_uid_col=allow_generate_uid_col,
            column_map=column_map,
            load_configs=load_configs,
            potential_uid_columns=potential_uid_columns,
            warnings=warnings,
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
