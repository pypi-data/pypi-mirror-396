import datetime
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
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitDatasetAnnotationParams")


@attrs.define
class CommitDatasetAnnotationParams:
    """
    Attributes:
        batch_uid (int):
        dataset_uid (int):
        source_uid (int):
        label_schema_uids (Union[Unset, List[int]]):
        ts (Union[Unset, datetime.datetime]):
    """

    batch_uid: int
    dataset_uid: int
    source_uid: int
    label_schema_uids: Union[Unset, List[int]] = UNSET
    ts: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        batch_uid = self.batch_uid
        dataset_uid = self.dataset_uid
        source_uid = self.source_uid
        label_schema_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.label_schema_uids, Unset):
            label_schema_uids = self.label_schema_uids

        ts: Union[Unset, str] = UNSET
        if not isinstance(self.ts, Unset):
            ts = self.ts.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batch_uid": batch_uid,
                "dataset_uid": dataset_uid,
                "source_uid": source_uid,
            }
        )
        if label_schema_uids is not UNSET:
            field_dict["label_schema_uids"] = label_schema_uids
        if ts is not UNSET:
            field_dict["ts"] = ts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        batch_uid = d.pop("batch_uid")

        dataset_uid = d.pop("dataset_uid")

        source_uid = d.pop("source_uid")

        _label_schema_uids = d.pop("label_schema_uids", UNSET)
        label_schema_uids = cast(
            List[int], UNSET if _label_schema_uids is None else _label_schema_uids
        )

        _ts = d.pop("ts", UNSET)
        _ts = UNSET if _ts is None else _ts
        ts: Union[Unset, datetime.datetime]
        if isinstance(_ts, Unset):
            ts = UNSET
        else:
            ts = isoparse(_ts)

        obj = cls(
            batch_uid=batch_uid,
            dataset_uid=dataset_uid,
            source_uid=source_uid,
            label_schema_uids=label_schema_uids,
            ts=ts,
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
