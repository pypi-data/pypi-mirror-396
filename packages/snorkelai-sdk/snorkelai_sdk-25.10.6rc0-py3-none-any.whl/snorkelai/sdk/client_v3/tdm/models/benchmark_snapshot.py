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

if TYPE_CHECKING:
    # fmt: off
    from ..models.benchmark import Benchmark  # noqa: F401
    from ..models.code_evaluator import CodeEvaluator  # noqa: F401
    from ..models.criteria import Criteria  # noqa: F401
    from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="BenchmarkSnapshot")


@attrs.define
class BenchmarkSnapshot:
    """
    Attributes:
        benchmark (Benchmark):
        criteria (List['Criteria']):
        evaluators (List[Union['CodeEvaluator', 'PromptEvaluator']]):
    """

    benchmark: "Benchmark"
    criteria: List["Criteria"]
    evaluators: List[Union["CodeEvaluator", "PromptEvaluator"]]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.benchmark import Benchmark  # noqa: F401
        from ..models.code_evaluator import CodeEvaluator  # noqa: F401
        from ..models.criteria import Criteria  # noqa: F401
        from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
        # fmt: on
        benchmark = self.benchmark.to_dict()
        criteria = []
        for criteria_item_data in self.criteria:
            criteria_item = criteria_item_data.to_dict()
            criteria.append(criteria_item)

        evaluators = []
        for evaluators_item_data in self.evaluators:
            evaluators_item: Dict[str, Any]
            if isinstance(evaluators_item_data, PromptEvaluator):
                evaluators_item = evaluators_item_data.to_dict()
            else:
                evaluators_item = evaluators_item_data.to_dict()

            evaluators.append(evaluators_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark": benchmark,
                "criteria": criteria,
                "evaluators": evaluators,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.benchmark import Benchmark  # noqa: F401
        from ..models.code_evaluator import CodeEvaluator  # noqa: F401
        from ..models.criteria import Criteria  # noqa: F401
        from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark = Benchmark.from_dict(d.pop("benchmark"))

        criteria = []
        _criteria = d.pop("criteria")
        for criteria_item_data in _criteria:
            criteria_item = Criteria.from_dict(criteria_item_data)

            criteria.append(criteria_item)

        evaluators = []
        _evaluators = d.pop("evaluators")
        for evaluators_item_data in _evaluators:

            def _parse_evaluators_item(
                data: object,
            ) -> Union["CodeEvaluator", "PromptEvaluator"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    evaluators_item_type_0 = PromptEvaluator.from_dict(data)

                    return evaluators_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                evaluators_item_type_1 = CodeEvaluator.from_dict(data)

                return evaluators_item_type_1

            evaluators_item = _parse_evaluators_item(evaluators_item_data)

            evaluators.append(evaluators_item)

        obj = cls(
            benchmark=benchmark,
            criteria=criteria,
            evaluators=evaluators,
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
