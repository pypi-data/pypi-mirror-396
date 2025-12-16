import datetime
from typing import (
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

T = TypeVar("T", bound="EvaluationMetric")


@attrs.define
class EvaluationMetric:
    """
    Attributes:
        metric_name (str):
        score_key (str):
        created_at (Union[Unset, datetime.datetime]):
        error (Union[Unset, str]):
        metric_key (Union[Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
        value (Union[Unset, float]):
        warning (Union[Unset, str]):
    """

    metric_name: str
    score_key: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    error: Union[Unset, str] = UNSET
    metric_key: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    value: Union[Unset, float] = UNSET
    warning: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metric_name = self.metric_name
        score_key = self.score_key
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        error = self.error
        metric_key = self.metric_key
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()
        value = self.value
        warning = self.warning

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric_name": metric_name,
                "score_key": score_key,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if error is not UNSET:
            field_dict["error"] = error
        if metric_key is not UNSET:
            field_dict["metric_key"] = metric_key
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if value is not UNSET:
            field_dict["value"] = value
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        metric_name = d.pop("metric_name")

        score_key = d.pop("score_key")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _error = d.pop("error", UNSET)
        error = UNSET if _error is None else _error

        _metric_key = d.pop("metric_key", UNSET)
        metric_key = UNSET if _metric_key is None else _metric_key

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _value = d.pop("value", UNSET)
        value = UNSET if _value is None else _value

        _warning = d.pop("warning", UNSET)
        warning = UNSET if _warning is None else _warning

        obj = cls(
            metric_name=metric_name,
            score_key=score_key,
            created_at=created_at,
            error=error,
            metric_key=metric_key,
            updated_at=updated_at,
            value=value,
            warning=warning,
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
