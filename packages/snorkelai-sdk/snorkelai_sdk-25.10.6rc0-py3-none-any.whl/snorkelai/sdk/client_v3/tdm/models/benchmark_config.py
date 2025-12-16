from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.benchmark_export_metadata import BenchmarkExportMetadata  # noqa: F401
    from ..models.criteria import Criteria  # noqa: F401
    from ..models.evaluator_with_prompt_configuration import (
        EvaluatorWithPromptConfiguration,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="BenchmarkConfig")


@attrs.define
class BenchmarkConfig:
    """
    Attributes:
        criteria (List['Criteria']):
        evaluators (List['EvaluatorWithPromptConfiguration']):
        metadata (BenchmarkExportMetadata):
    """

    criteria: List["Criteria"]
    evaluators: List["EvaluatorWithPromptConfiguration"]
    metadata: "BenchmarkExportMetadata"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.benchmark_export_metadata import (
            BenchmarkExportMetadata,  # noqa: F401
        )
        from ..models.criteria import Criteria  # noqa: F401
        from ..models.evaluator_with_prompt_configuration import (
            EvaluatorWithPromptConfiguration,  # noqa: F401
        )
        # fmt: on
        criteria = []
        for criteria_item_data in self.criteria:
            criteria_item = criteria_item_data.to_dict()
            criteria.append(criteria_item)

        evaluators = []
        for evaluators_item_data in self.evaluators:
            evaluators_item = evaluators_item_data.to_dict()
            evaluators.append(evaluators_item)

        metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria": criteria,
                "evaluators": evaluators,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.benchmark_export_metadata import (
            BenchmarkExportMetadata,  # noqa: F401
        )
        from ..models.criteria import Criteria  # noqa: F401
        from ..models.evaluator_with_prompt_configuration import (
            EvaluatorWithPromptConfiguration,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        criteria = []
        _criteria = d.pop("criteria")
        for criteria_item_data in _criteria:
            criteria_item = Criteria.from_dict(criteria_item_data)

            criteria.append(criteria_item)

        evaluators = []
        _evaluators = d.pop("evaluators")
        for evaluators_item_data in _evaluators:
            evaluators_item = EvaluatorWithPromptConfiguration.from_dict(
                evaluators_item_data
            )

            evaluators.append(evaluators_item)

        metadata = BenchmarkExportMetadata.from_dict(d.pop("metadata"))

        obj = cls(
            criteria=criteria,
            evaluators=evaluators,
            metadata=metadata,
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
