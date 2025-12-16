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
    from ..models.input_warning import InputWarning  # noqa: F401
    from ..models.single_source_analysis_result_column_map import (
        SingleSourceAnalysisResultColumnMap,  # noqa: F401
    )
    from ..models.single_source_analysis_result_failed_jobs_item import (
        SingleSourceAnalysisResultFailedJobsItem,  # noqa: F401
    )
    from ..models.single_source_analysis_result_failed_requests_item import (
        SingleSourceAnalysisResultFailedRequestsItem,  # noqa: F401
    )
    from ..models.single_source_analysis_result_load_configs_item import (
        SingleSourceAnalysisResultLoadConfigsItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SingleSourceAnalysisResult")


@attrs.define
class SingleSourceAnalysisResult:
    """Results from analyzing a single data source.

    Attributes:
        allow_generate_uid_col (Union[Unset, bool]):  Default: False.
        column_map (Union[Unset, SingleSourceAnalysisResultColumnMap]):
        failed_jobs (Union[Unset, List['SingleSourceAnalysisResultFailedJobsItem']]):
        failed_requests (Union[Unset, List['SingleSourceAnalysisResultFailedRequestsItem']]):
        load_configs (Union[Unset, List['SingleSourceAnalysisResultLoadConfigsItem']]):
        potential_uid_columns (Union[Unset, List[str]]):
        warnings (Union[Unset, List['InputWarning']]):
    """

    allow_generate_uid_col: Union[Unset, bool] = False
    column_map: Union[Unset, "SingleSourceAnalysisResultColumnMap"] = UNSET
    failed_jobs: Union[Unset, List["SingleSourceAnalysisResultFailedJobsItem"]] = UNSET
    failed_requests: Union[
        Unset, List["SingleSourceAnalysisResultFailedRequestsItem"]
    ] = UNSET
    load_configs: Union[Unset, List["SingleSourceAnalysisResultLoadConfigsItem"]] = (
        UNSET
    )
    potential_uid_columns: Union[Unset, List[str]] = UNSET
    warnings: Union[Unset, List["InputWarning"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.input_warning import InputWarning  # noqa: F401
        from ..models.single_source_analysis_result_column_map import (
            SingleSourceAnalysisResultColumnMap,  # noqa: F401
        )
        from ..models.single_source_analysis_result_failed_jobs_item import (
            SingleSourceAnalysisResultFailedJobsItem,  # noqa: F401
        )
        from ..models.single_source_analysis_result_failed_requests_item import (
            SingleSourceAnalysisResultFailedRequestsItem,  # noqa: F401
        )
        from ..models.single_source_analysis_result_load_configs_item import (
            SingleSourceAnalysisResultLoadConfigsItem,  # noqa: F401
        )
        # fmt: on
        allow_generate_uid_col = self.allow_generate_uid_col
        column_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.column_map, Unset):
            column_map = self.column_map.to_dict()
        failed_jobs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.failed_jobs, Unset):
            failed_jobs = []
            for failed_jobs_item_data in self.failed_jobs:
                failed_jobs_item = failed_jobs_item_data.to_dict()
                failed_jobs.append(failed_jobs_item)

        failed_requests: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.failed_requests, Unset):
            failed_requests = []
            for failed_requests_item_data in self.failed_requests:
                failed_requests_item = failed_requests_item_data.to_dict()
                failed_requests.append(failed_requests_item)

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
        field_dict.update({})
        if allow_generate_uid_col is not UNSET:
            field_dict["allow_generate_uid_col"] = allow_generate_uid_col
        if column_map is not UNSET:
            field_dict["column_map"] = column_map
        if failed_jobs is not UNSET:
            field_dict["failed_jobs"] = failed_jobs
        if failed_requests is not UNSET:
            field_dict["failed_requests"] = failed_requests
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
        from ..models.input_warning import InputWarning  # noqa: F401
        from ..models.single_source_analysis_result_column_map import (
            SingleSourceAnalysisResultColumnMap,  # noqa: F401
        )
        from ..models.single_source_analysis_result_failed_jobs_item import (
            SingleSourceAnalysisResultFailedJobsItem,  # noqa: F401
        )
        from ..models.single_source_analysis_result_failed_requests_item import (
            SingleSourceAnalysisResultFailedRequestsItem,  # noqa: F401
        )
        from ..models.single_source_analysis_result_load_configs_item import (
            SingleSourceAnalysisResultLoadConfigsItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _allow_generate_uid_col = d.pop("allow_generate_uid_col", UNSET)
        allow_generate_uid_col = (
            UNSET if _allow_generate_uid_col is None else _allow_generate_uid_col
        )

        _column_map = d.pop("column_map", UNSET)
        _column_map = UNSET if _column_map is None else _column_map
        column_map: Union[Unset, SingleSourceAnalysisResultColumnMap]
        if isinstance(_column_map, Unset):
            column_map = UNSET
        else:
            column_map = SingleSourceAnalysisResultColumnMap.from_dict(_column_map)

        _failed_jobs = d.pop("failed_jobs", UNSET)
        failed_jobs = []
        _failed_jobs = UNSET if _failed_jobs is None else _failed_jobs
        for failed_jobs_item_data in _failed_jobs or []:
            failed_jobs_item = SingleSourceAnalysisResultFailedJobsItem.from_dict(
                failed_jobs_item_data
            )

            failed_jobs.append(failed_jobs_item)

        _failed_requests = d.pop("failed_requests", UNSET)
        failed_requests = []
        _failed_requests = UNSET if _failed_requests is None else _failed_requests
        for failed_requests_item_data in _failed_requests or []:
            failed_requests_item = (
                SingleSourceAnalysisResultFailedRequestsItem.from_dict(
                    failed_requests_item_data
                )
            )

            failed_requests.append(failed_requests_item)

        _load_configs = d.pop("load_configs", UNSET)
        load_configs = []
        _load_configs = UNSET if _load_configs is None else _load_configs
        for load_configs_item_data in _load_configs or []:
            load_configs_item = SingleSourceAnalysisResultLoadConfigsItem.from_dict(
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
            allow_generate_uid_col=allow_generate_uid_col,
            column_map=column_map,
            failed_jobs=failed_jobs,
            failed_requests=failed_requests,
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
