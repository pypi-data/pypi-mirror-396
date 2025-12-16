from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..models.criteria_filter_operator import CriteriaFilterOperator
from ..models.evaluation_score_type import EvaluationScoreType
from ..models.filter_transform_filter_types import FilterTransformFilterTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="CriteriaFilterSchema")


@attrs.define
class CriteriaFilterSchema:
    """
    Attributes:
        criteria_uid (int):
        operator (CriteriaFilterOperator): Operators available for criteria filters.
        benchmark_execution_uid (Union[Unset, int]):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        prompt_execution_uid (Union[Unset, int]):
        score_type (Union[Unset, EvaluationScoreType]):
        transform_config_type (Union[Literal['criteria_filter_schema'], Unset]):  Default: 'criteria_filter_schema'.
        value (Union[None, Unset, bool, float, int, str]):
    """

    criteria_uid: int
    operator: CriteriaFilterOperator
    benchmark_execution_uid: Union[Unset, int] = UNSET
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    prompt_execution_uid: Union[Unset, int] = UNSET
    score_type: Union[Unset, EvaluationScoreType] = UNSET
    transform_config_type: Union[Literal["criteria_filter_schema"], Unset] = (
        "criteria_filter_schema"
    )
    value: Union[None, Unset, bool, float, int, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        criteria_uid = self.criteria_uid
        operator = self.operator.value
        benchmark_execution_uid = self.benchmark_execution_uid
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        prompt_execution_uid = self.prompt_execution_uid
        score_type: Union[Unset, str] = UNSET
        if not isinstance(self.score_type, Unset):
            score_type = self.score_type.value

        transform_config_type = self.transform_config_type
        value: Union[None, Unset, bool, float, int, str]
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_uid": criteria_uid,
                "operator": operator,
            }
        )
        if benchmark_execution_uid is not UNSET:
            field_dict["benchmark_execution_uid"] = benchmark_execution_uid
        if filter_type is not UNSET:
            field_dict["filter_type"] = filter_type
        if prompt_execution_uid is not UNSET:
            field_dict["prompt_execution_uid"] = prompt_execution_uid
        if score_type is not UNSET:
            field_dict["score_type"] = score_type
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        criteria_uid = d.pop("criteria_uid")

        operator = CriteriaFilterOperator(d.pop("operator"))

        _benchmark_execution_uid = d.pop("benchmark_execution_uid", UNSET)
        benchmark_execution_uid = (
            UNSET if _benchmark_execution_uid is None else _benchmark_execution_uid
        )

        _filter_type = d.pop("filter_type", UNSET)
        _filter_type = UNSET if _filter_type is None else _filter_type
        filter_type: Union[Unset, FilterTransformFilterTypes]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = FilterTransformFilterTypes(_filter_type)

        _prompt_execution_uid = d.pop("prompt_execution_uid", UNSET)
        prompt_execution_uid = (
            UNSET if _prompt_execution_uid is None else _prompt_execution_uid
        )

        _score_type = d.pop("score_type", UNSET)
        _score_type = UNSET if _score_type is None else _score_type
        score_type: Union[Unset, EvaluationScoreType]
        if isinstance(_score_type, Unset):
            score_type = UNSET
        else:
            score_type = EvaluationScoreType(_score_type)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        _value = d.pop("value", UNSET)

        def _parse_value(data: object) -> Union[None, Unset, bool, float, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool, float, int, str], data)

        value = _parse_value(UNSET if _value is None else _value)

        obj = cls(
            criteria_uid=criteria_uid,
            operator=operator,
            benchmark_execution_uid=benchmark_execution_uid,
            filter_type=filter_type,
            prompt_execution_uid=prompt_execution_uid,
            score_type=score_type,
            transform_config_type=transform_config_type,
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
