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

from ..models.criteria_filter_operator import CriteriaFilterOperator
from ..models.evaluation_score_type import EvaluationScoreType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.option_model import OptionModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ScoreTypeOperators")


@attrs.define
class ScoreTypeOperators:
    """Model for a score type with its supported operators.

    This model defines the relationship between a specific evaluation score type
    (like 'SCORE', 'RATIONALE', or 'AGREEMENT') and the filter operators that can be
    applied to values of that score type. Different score types support different
    sets of operators based on their data characteristics.

        Attributes:
            operators (List[CriteriaFilterOperator]):
            score_type (EvaluationScoreType):
            value_options (Union[Unset, List['OptionModel']]):
    """

    operators: List[CriteriaFilterOperator]
    score_type: EvaluationScoreType
    value_options: Union[Unset, List["OptionModel"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        operators = []
        for operators_item_data in self.operators:
            operators_item = operators_item_data.value
            operators.append(operators_item)

        score_type = self.score_type.value
        value_options: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.value_options, Unset):
            value_options = []
            for value_options_item_data in self.value_options:
                value_options_item = value_options_item_data.to_dict()
                value_options.append(value_options_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "operators": operators,
                "score_type": score_type,
            }
        )
        if value_options is not UNSET:
            field_dict["value_options"] = value_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        operators = []
        _operators = d.pop("operators")
        for operators_item_data in _operators:
            operators_item = CriteriaFilterOperator(operators_item_data)

            operators.append(operators_item)

        score_type = EvaluationScoreType(d.pop("score_type"))

        _value_options = d.pop("value_options", UNSET)
        value_options = []
        _value_options = UNSET if _value_options is None else _value_options
        for value_options_item_data in _value_options or []:
            value_options_item = OptionModel.from_dict(value_options_item_data)

            value_options.append(value_options_item)

        obj = cls(
            operators=operators,
            score_type=score_type,
            value_options=value_options,
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
