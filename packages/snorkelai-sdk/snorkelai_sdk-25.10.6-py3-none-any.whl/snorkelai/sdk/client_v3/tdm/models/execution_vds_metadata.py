from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.splits import Splits
from ..types import UNSET, Unset

T = TypeVar("T", bound="ExecutionVDSMetadata")


@attrs.define
class ExecutionVDSMetadata:
    """
    Attributes:
        filter_config_str (Union[Unset, str]):
        first_n_indexes (Union[Unset, int]):
        first_n_traces (Union[Unset, int]):
        source_vds_uid (Union[Unset, int]):
        splits (Union[Unset, List[Splits]]):
    """

    filter_config_str: Union[Unset, str] = UNSET
    first_n_indexes: Union[Unset, int] = UNSET
    first_n_traces: Union[Unset, int] = UNSET
    source_vds_uid: Union[Unset, int] = UNSET
    splits: Union[Unset, List[Splits]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_config_str = self.filter_config_str
        first_n_indexes = self.first_n_indexes
        first_n_traces = self.first_n_traces
        source_vds_uid = self.source_vds_uid
        splits: Union[Unset, List[str]] = UNSET
        if not isinstance(self.splits, Unset):
            splits = []
            for splits_item_data in self.splits:
                splits_item = splits_item_data.value
                splits.append(splits_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_config_str is not UNSET:
            field_dict["filter_config_str"] = filter_config_str
        if first_n_indexes is not UNSET:
            field_dict["first_n_indexes"] = first_n_indexes
        if first_n_traces is not UNSET:
            field_dict["first_n_traces"] = first_n_traces
        if source_vds_uid is not UNSET:
            field_dict["source_vds_uid"] = source_vds_uid
        if splits is not UNSET:
            field_dict["splits"] = splits

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _filter_config_str = d.pop("filter_config_str", UNSET)
        filter_config_str = UNSET if _filter_config_str is None else _filter_config_str

        _first_n_indexes = d.pop("first_n_indexes", UNSET)
        first_n_indexes = UNSET if _first_n_indexes is None else _first_n_indexes

        _first_n_traces = d.pop("first_n_traces", UNSET)
        first_n_traces = UNSET if _first_n_traces is None else _first_n_traces

        _source_vds_uid = d.pop("source_vds_uid", UNSET)
        source_vds_uid = UNSET if _source_vds_uid is None else _source_vds_uid

        _splits = d.pop("splits", UNSET)
        splits = []
        _splits = UNSET if _splits is None else _splits
        for splits_item_data in _splits or []:
            splits_item = Splits(splits_item_data)

            splits.append(splits_item)

        obj = cls(
            filter_config_str=filter_config_str,
            first_n_indexes=first_n_indexes,
            first_n_traces=first_n_traces,
            source_vds_uid=source_vds_uid,
            splits=splits,
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
