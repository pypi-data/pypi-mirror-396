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
    from ..models.analyze_data_sources_request_col_fill_values import (
        AnalyzeDataSourcesRequestColFillValues,  # noqa: F401
    )
    from ..models.path_with_split import PathWithSplit  # noqa: F401
    from ..models.static_asset_col_info import StaticAssetColInfo  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnalyzeDataSourcesRequest")


@attrs.define
class AnalyzeDataSourcesRequest:
    """
    Attributes:
        source_type (str):
        col_fill_values (Union[Unset, AnalyzeDataSourcesRequestColFillValues]):
        credential_kwargs (Union[Unset, str]):
        data_connector_config_uid (Union[Unset, int]):
        datestamp (Union[Unset, str]):
        load_to_model_nodes (Union[Unset, bool]):  Default: False.
        paths_with_split (Union[Unset, List['PathWithSplit']]):
        reader_kwargs (Union[Unset, str]):
        run_async (Union[Unset, bool]):  Default: False.
        run_datasource_checks (Union[Unset, bool]):  Default: False.
        scheduler (Union[Unset, str]):
        skip_repartition (Union[Unset, bool]):
        source_uid (Union[Unset, int]):
        static_asset_col_info (Union[Unset, StaticAssetColInfo]):
        uid_col (Union[Unset, str]):
    """

    source_type: str
    col_fill_values: Union[Unset, "AnalyzeDataSourcesRequestColFillValues"] = UNSET
    credential_kwargs: Union[Unset, str] = UNSET
    data_connector_config_uid: Union[Unset, int] = UNSET
    datestamp: Union[Unset, str] = UNSET
    load_to_model_nodes: Union[Unset, bool] = False
    paths_with_split: Union[Unset, List["PathWithSplit"]] = UNSET
    reader_kwargs: Union[Unset, str] = UNSET
    run_async: Union[Unset, bool] = False
    run_datasource_checks: Union[Unset, bool] = False
    scheduler: Union[Unset, str] = UNSET
    skip_repartition: Union[Unset, bool] = UNSET
    source_uid: Union[Unset, int] = UNSET
    static_asset_col_info: Union[Unset, "StaticAssetColInfo"] = UNSET
    uid_col: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.analyze_data_sources_request_col_fill_values import (
            AnalyzeDataSourcesRequestColFillValues,  # noqa: F401
        )
        from ..models.path_with_split import PathWithSplit  # noqa: F401
        from ..models.static_asset_col_info import StaticAssetColInfo  # noqa: F401
        # fmt: on
        source_type = self.source_type
        col_fill_values: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.col_fill_values, Unset):
            col_fill_values = self.col_fill_values.to_dict()
        credential_kwargs = self.credential_kwargs
        data_connector_config_uid = self.data_connector_config_uid
        datestamp = self.datestamp
        load_to_model_nodes = self.load_to_model_nodes
        paths_with_split: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.paths_with_split, Unset):
            paths_with_split = []
            for paths_with_split_item_data in self.paths_with_split:
                paths_with_split_item = paths_with_split_item_data.to_dict()
                paths_with_split.append(paths_with_split_item)

        reader_kwargs = self.reader_kwargs
        run_async = self.run_async
        run_datasource_checks = self.run_datasource_checks
        scheduler = self.scheduler
        skip_repartition = self.skip_repartition
        source_uid = self.source_uid
        static_asset_col_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.static_asset_col_info, Unset):
            static_asset_col_info = self.static_asset_col_info.to_dict()
        uid_col = self.uid_col

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_type": source_type,
            }
        )
        if col_fill_values is not UNSET:
            field_dict["col_fill_values"] = col_fill_values
        if credential_kwargs is not UNSET:
            field_dict["credential_kwargs"] = credential_kwargs
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if datestamp is not UNSET:
            field_dict["datestamp"] = datestamp
        if load_to_model_nodes is not UNSET:
            field_dict["load_to_model_nodes"] = load_to_model_nodes
        if paths_with_split is not UNSET:
            field_dict["paths_with_split"] = paths_with_split
        if reader_kwargs is not UNSET:
            field_dict["reader_kwargs"] = reader_kwargs
        if run_async is not UNSET:
            field_dict["run_async"] = run_async
        if run_datasource_checks is not UNSET:
            field_dict["run_datasource_checks"] = run_datasource_checks
        if scheduler is not UNSET:
            field_dict["scheduler"] = scheduler
        if skip_repartition is not UNSET:
            field_dict["skip_repartition"] = skip_repartition
        if source_uid is not UNSET:
            field_dict["source_uid"] = source_uid
        if static_asset_col_info is not UNSET:
            field_dict["static_asset_col_info"] = static_asset_col_info
        if uid_col is not UNSET:
            field_dict["uid_col"] = uid_col

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.analyze_data_sources_request_col_fill_values import (
            AnalyzeDataSourcesRequestColFillValues,  # noqa: F401
        )
        from ..models.path_with_split import PathWithSplit  # noqa: F401
        from ..models.static_asset_col_info import StaticAssetColInfo  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        source_type = d.pop("source_type")

        _col_fill_values = d.pop("col_fill_values", UNSET)
        _col_fill_values = UNSET if _col_fill_values is None else _col_fill_values
        col_fill_values: Union[Unset, AnalyzeDataSourcesRequestColFillValues]
        if isinstance(_col_fill_values, Unset):
            col_fill_values = UNSET
        else:
            col_fill_values = AnalyzeDataSourcesRequestColFillValues.from_dict(
                _col_fill_values
            )

        _credential_kwargs = d.pop("credential_kwargs", UNSET)
        credential_kwargs = UNSET if _credential_kwargs is None else _credential_kwargs

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _datestamp = d.pop("datestamp", UNSET)
        datestamp = UNSET if _datestamp is None else _datestamp

        _load_to_model_nodes = d.pop("load_to_model_nodes", UNSET)
        load_to_model_nodes = (
            UNSET if _load_to_model_nodes is None else _load_to_model_nodes
        )

        _paths_with_split = d.pop("paths_with_split", UNSET)
        paths_with_split = []
        _paths_with_split = UNSET if _paths_with_split is None else _paths_with_split
        for paths_with_split_item_data in _paths_with_split or []:
            paths_with_split_item = PathWithSplit.from_dict(paths_with_split_item_data)

            paths_with_split.append(paths_with_split_item)

        _reader_kwargs = d.pop("reader_kwargs", UNSET)
        reader_kwargs = UNSET if _reader_kwargs is None else _reader_kwargs

        _run_async = d.pop("run_async", UNSET)
        run_async = UNSET if _run_async is None else _run_async

        _run_datasource_checks = d.pop("run_datasource_checks", UNSET)
        run_datasource_checks = (
            UNSET if _run_datasource_checks is None else _run_datasource_checks
        )

        _scheduler = d.pop("scheduler", UNSET)
        scheduler = UNSET if _scheduler is None else _scheduler

        _skip_repartition = d.pop("skip_repartition", UNSET)
        skip_repartition = UNSET if _skip_repartition is None else _skip_repartition

        _source_uid = d.pop("source_uid", UNSET)
        source_uid = UNSET if _source_uid is None else _source_uid

        _static_asset_col_info = d.pop("static_asset_col_info", UNSET)
        _static_asset_col_info = (
            UNSET if _static_asset_col_info is None else _static_asset_col_info
        )
        static_asset_col_info: Union[Unset, StaticAssetColInfo]
        if isinstance(_static_asset_col_info, Unset):
            static_asset_col_info = UNSET
        else:
            static_asset_col_info = StaticAssetColInfo.from_dict(_static_asset_col_info)

        _uid_col = d.pop("uid_col", UNSET)
        uid_col = UNSET if _uid_col is None else _uid_col

        obj = cls(
            source_type=source_type,
            col_fill_values=col_fill_values,
            credential_kwargs=credential_kwargs,
            data_connector_config_uid=data_connector_config_uid,
            datestamp=datestamp,
            load_to_model_nodes=load_to_model_nodes,
            paths_with_split=paths_with_split,
            reader_kwargs=reader_kwargs,
            run_async=run_async,
            run_datasource_checks=run_datasource_checks,
            scheduler=scheduler,
            skip_repartition=skip_repartition,
            source_uid=source_uid,
            static_asset_col_info=static_asset_col_info,
            uid_col=uid_col,
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
