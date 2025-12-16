from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.datasource_type import DatasourceType
from ..models.split import Split
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.split_by_file_datasource_ingestion_request_col_fill_values import (
        SplitByFileDatasourceIngestionRequestColFillValues,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SplitByFileDatasourceIngestionRequest")


@attrs.define
class SplitByFileDatasourceIngestionRequest:
    """Request model for ingesting a single data source with explicit splits.

    Attributes:
        dataset_uid (int):
        source (str): Path, query, or other identifier for the data source
        source_type (DatasourceType): Types of data sources that can be connected to.
        split (Split): Valid dataset split types.
        type (Literal['structured']):
        col_fill_values (Union[Unset, SplitByFileDatasourceIngestionRequestColFillValues]):
        data_connector_config_uid (Union[Unset, int]):
        load_to_model_nodes (Union[Unset, bool]):  Default: False.
        source_uid (Union[Unset, int]):
        uid_col (Union[Unset, str]):
    """

    dataset_uid: int
    source: str
    source_type: DatasourceType
    split: Split
    type: Literal["structured"]
    col_fill_values: Union[
        Unset, "SplitByFileDatasourceIngestionRequestColFillValues"
    ] = UNSET
    data_connector_config_uid: Union[Unset, int] = UNSET
    load_to_model_nodes: Union[Unset, bool] = False
    source_uid: Union[Unset, int] = UNSET
    uid_col: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.split_by_file_datasource_ingestion_request_col_fill_values import (
            SplitByFileDatasourceIngestionRequestColFillValues,  # noqa: F401
        )
        # fmt: on
        dataset_uid = self.dataset_uid
        source = self.source
        source_type = self.source_type.value
        split = self.split.value
        type = self.type
        col_fill_values: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.col_fill_values, Unset):
            col_fill_values = self.col_fill_values.to_dict()
        data_connector_config_uid = self.data_connector_config_uid
        load_to_model_nodes = self.load_to_model_nodes
        source_uid = self.source_uid
        uid_col = self.uid_col

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "source": source,
                "source_type": source_type,
                "split": split,
                "type": type,
            }
        )
        if col_fill_values is not UNSET:
            field_dict["col_fill_values"] = col_fill_values
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if load_to_model_nodes is not UNSET:
            field_dict["load_to_model_nodes"] = load_to_model_nodes
        if source_uid is not UNSET:
            field_dict["source_uid"] = source_uid
        if uid_col is not UNSET:
            field_dict["uid_col"] = uid_col

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.split_by_file_datasource_ingestion_request_col_fill_values import (
            SplitByFileDatasourceIngestionRequestColFillValues,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        source = d.pop("source")

        source_type = DatasourceType(d.pop("source_type"))

        split = Split(d.pop("split"))

        type = d.pop("type")

        _col_fill_values = d.pop("col_fill_values", UNSET)
        _col_fill_values = UNSET if _col_fill_values is None else _col_fill_values
        col_fill_values: Union[
            Unset, SplitByFileDatasourceIngestionRequestColFillValues
        ]
        if isinstance(_col_fill_values, Unset):
            col_fill_values = UNSET
        else:
            col_fill_values = (
                SplitByFileDatasourceIngestionRequestColFillValues.from_dict(
                    _col_fill_values
                )
            )

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _load_to_model_nodes = d.pop("load_to_model_nodes", UNSET)
        load_to_model_nodes = (
            UNSET if _load_to_model_nodes is None else _load_to_model_nodes
        )

        _source_uid = d.pop("source_uid", UNSET)
        source_uid = UNSET if _source_uid is None else _source_uid

        _uid_col = d.pop("uid_col", UNSET)
        uid_col = UNSET if _uid_col is None else _uid_col

        obj = cls(
            dataset_uid=dataset_uid,
            source=source,
            source_type=source_type,
            split=split,
            type=type,
            col_fill_values=col_fill_values,
            data_connector_config_uid=data_connector_config_uid,
            load_to_model_nodes=load_to_model_nodes,
            source_uid=source_uid,
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
