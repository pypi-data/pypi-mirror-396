from typing import (
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

T = TypeVar("T", bound="AggregateDatasetAnnotationsParams")


@attrs.define
class AggregateDatasetAnnotationsParams:
    """
    Attributes:
        dataset_batch_uid (int):
        dataset_uid (int):
        label_schema_uids (Union[Unset, List[int]]):
        source_name (Union[Unset, str]):
        source_uids (Union[Unset, List[int]]):
        strategy (Union[Unset, str]):
    """

    dataset_batch_uid: int
    dataset_uid: int
    label_schema_uids: Union[Unset, List[int]] = UNSET
    source_name: Union[Unset, str] = UNSET
    source_uids: Union[Unset, List[int]] = UNSET
    strategy: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_batch_uid = self.dataset_batch_uid
        dataset_uid = self.dataset_uid
        label_schema_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.label_schema_uids, Unset):
            label_schema_uids = self.label_schema_uids

        source_name = self.source_name
        source_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.source_uids, Unset):
            source_uids = self.source_uids

        strategy = self.strategy

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_batch_uid": dataset_batch_uid,
                "dataset_uid": dataset_uid,
            }
        )
        if label_schema_uids is not UNSET:
            field_dict["label_schema_uids"] = label_schema_uids
        if source_name is not UNSET:
            field_dict["source_name"] = source_name
        if source_uids is not UNSET:
            field_dict["source_uids"] = source_uids
        if strategy is not UNSET:
            field_dict["strategy"] = strategy

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_batch_uid = d.pop("dataset_batch_uid")

        dataset_uid = d.pop("dataset_uid")

        _label_schema_uids = d.pop("label_schema_uids", UNSET)
        label_schema_uids = cast(
            List[int], UNSET if _label_schema_uids is None else _label_schema_uids
        )

        _source_name = d.pop("source_name", UNSET)
        source_name = UNSET if _source_name is None else _source_name

        _source_uids = d.pop("source_uids", UNSET)
        source_uids = cast(List[int], UNSET if _source_uids is None else _source_uids)

        _strategy = d.pop("strategy", UNSET)
        strategy = UNSET if _strategy is None else _strategy

        obj = cls(
            dataset_batch_uid=dataset_batch_uid,
            dataset_uid=dataset_uid,
            label_schema_uids=label_schema_uids,
            source_name=source_name,
            source_uids=source_uids,
            strategy=strategy,
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
