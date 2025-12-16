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

from ..models.evaluation_score_type import EvaluationScoreType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EvaluationScore")


@attrs.define
class EvaluationScore:
    """
    Attributes:
        criteria_uid (int):
        dataset_uid (int):
        type (EvaluationScoreType):
        x_uid (str):
        created_at (Union[Unset, datetime.datetime]):
        error (Union[Unset, str]):
        score_key (Union[Unset, str]):
        value (Union[None, Unset, float, int, str]):
    """

    criteria_uid: int
    dataset_uid: int
    type: EvaluationScoreType
    x_uid: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    error: Union[Unset, str] = UNSET
    score_key: Union[Unset, str] = UNSET
    value: Union[None, Unset, float, int, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        criteria_uid = self.criteria_uid
        dataset_uid = self.dataset_uid
        type = self.type.value
        x_uid = self.x_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        error = self.error
        score_key = self.score_key
        value: Union[None, Unset, float, int, str]
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_uid": criteria_uid,
                "dataset_uid": dataset_uid,
                "type": type,
                "x_uid": x_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if error is not UNSET:
            field_dict["error"] = error
        if score_key is not UNSET:
            field_dict["score_key"] = score_key
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        criteria_uid = d.pop("criteria_uid")

        dataset_uid = d.pop("dataset_uid")

        type = EvaluationScoreType(d.pop("type"))

        x_uid = d.pop("x_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _error = d.pop("error", UNSET)
        error = UNSET if _error is None else _error

        _score_key = d.pop("score_key", UNSET)
        score_key = UNSET if _score_key is None else _score_key

        _value = d.pop("value", UNSET)

        def _parse_value(data: object) -> Union[None, Unset, float, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float, int, str], data)

        value = _parse_value(UNSET if _value is None else _value)

        obj = cls(
            criteria_uid=criteria_uid,
            dataset_uid=dataset_uid,
            type=type,
            x_uid=x_uid,
            created_at=created_at,
            error=error,
            score_key=score_key,
            value=value,
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
