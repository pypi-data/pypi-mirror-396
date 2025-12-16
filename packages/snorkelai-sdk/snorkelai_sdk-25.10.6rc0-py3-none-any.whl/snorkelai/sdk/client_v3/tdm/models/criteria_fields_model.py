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
    from ..models.score_type_operators import ScoreTypeOperators  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CriteriaFieldsModel")


@attrs.define
class CriteriaFieldsModel:
    """Model for criteria fields with their available operators.

    Attributes:
        criteria_type (str):
        criteria_uid (int):
        display_name (str):
        score_type_operators (List['ScoreTypeOperators']):
        benchmark_execution_uid (Union[Unset, int]):
        prompt_execution_uid (Union[Unset, int]):
    """

    criteria_type: str
    criteria_uid: int
    display_name: str
    score_type_operators: List["ScoreTypeOperators"]
    benchmark_execution_uid: Union[Unset, int] = UNSET
    prompt_execution_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.score_type_operators import ScoreTypeOperators  # noqa: F401
        # fmt: on
        criteria_type = self.criteria_type
        criteria_uid = self.criteria_uid
        display_name = self.display_name
        score_type_operators = []
        for score_type_operators_item_data in self.score_type_operators:
            score_type_operators_item = score_type_operators_item_data.to_dict()
            score_type_operators.append(score_type_operators_item)

        benchmark_execution_uid = self.benchmark_execution_uid
        prompt_execution_uid = self.prompt_execution_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_type": criteria_type,
                "criteria_uid": criteria_uid,
                "display_name": display_name,
                "score_type_operators": score_type_operators,
            }
        )
        if benchmark_execution_uid is not UNSET:
            field_dict["benchmark_execution_uid"] = benchmark_execution_uid
        if prompt_execution_uid is not UNSET:
            field_dict["prompt_execution_uid"] = prompt_execution_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.score_type_operators import ScoreTypeOperators  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        criteria_type = d.pop("criteria_type")

        criteria_uid = d.pop("criteria_uid")

        display_name = d.pop("display_name")

        score_type_operators = []
        _score_type_operators = d.pop("score_type_operators")
        for score_type_operators_item_data in _score_type_operators:
            score_type_operators_item = ScoreTypeOperators.from_dict(
                score_type_operators_item_data
            )

            score_type_operators.append(score_type_operators_item)

        _benchmark_execution_uid = d.pop("benchmark_execution_uid", UNSET)
        benchmark_execution_uid = (
            UNSET if _benchmark_execution_uid is None else _benchmark_execution_uid
        )

        _prompt_execution_uid = d.pop("prompt_execution_uid", UNSET)
        prompt_execution_uid = (
            UNSET if _prompt_execution_uid is None else _prompt_execution_uid
        )

        obj = cls(
            criteria_type=criteria_type,
            criteria_uid=criteria_uid,
            display_name=display_name,
            score_type_operators=score_type_operators,
            benchmark_execution_uid=benchmark_execution_uid,
            prompt_execution_uid=prompt_execution_uid,
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
