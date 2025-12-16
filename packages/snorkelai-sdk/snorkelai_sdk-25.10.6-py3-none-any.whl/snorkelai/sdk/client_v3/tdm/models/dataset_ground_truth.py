import datetime
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
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DatasetGroundTruth")


@attrs.define
class DatasetGroundTruth:
    """
    Attributes:
        labels (List['LabelSchemaLabels']):
        x_uid (str):
        committed_by (Union[Unset, int]):
        ts (Union[Unset, datetime.datetime]):
    """

    labels: List["LabelSchemaLabels"]
    x_uid: str
    committed_by: Union[Unset, int] = UNSET
    ts: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
        # fmt: on
        labels = []
        for labels_item_data in self.labels:
            labels_item = labels_item_data.to_dict()
            labels.append(labels_item)

        x_uid = self.x_uid
        committed_by = self.committed_by
        ts: Union[Unset, str] = UNSET
        if not isinstance(self.ts, Unset):
            ts = self.ts.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "labels": labels,
                "x_uid": x_uid,
            }
        )
        if committed_by is not UNSET:
            field_dict["committed_by"] = committed_by
        if ts is not UNSET:
            field_dict["ts"] = ts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        labels = []
        _labels = d.pop("labels")
        for labels_item_data in _labels:
            labels_item = LabelSchemaLabels.from_dict(labels_item_data)

            labels.append(labels_item)

        x_uid = d.pop("x_uid")

        _committed_by = d.pop("committed_by", UNSET)
        committed_by = UNSET if _committed_by is None else _committed_by

        _ts = d.pop("ts", UNSET)
        _ts = UNSET if _ts is None else _ts
        ts: Union[Unset, datetime.datetime]
        if isinstance(_ts, Unset):
            ts = UNSET
        else:
            ts = isoparse(_ts)

        obj = cls(
            labels=labels,
            x_uid=x_uid,
            committed_by=committed_by,
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
