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
    from ..models.executions_response_criterion_error_score_count_by_split import (
        ExecutionsResponseCriterionErrorScoreCountBySplit,  # noqa: F401
    )
    from ..models.executions_response_criterion_no_score_count_by_split import (
        ExecutionsResponseCriterionNoScoreCountBySplit,  # noqa: F401
    )
    from ..models.executions_response_criterion_prompt_execution_by_split import (
        ExecutionsResponseCriterionPromptExecutionBySplit,  # noqa: F401
    )
    from ..models.output_format import OutputFormat  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ExecutionsResponseCriterion")


@attrs.define
class ExecutionsResponseCriterion:
    """
    Attributes:
        benchmark_uid (int):
        criteria_uid (int):
        evaluator_type (str):
        name (str):
        state (str):
        code_execution_uid (Union[Unset, int]):
        description (Union[Unset, str]):
        error_score_count_by_split (Union[Unset, ExecutionsResponseCriterionErrorScoreCountBySplit]):
        filter_config (Union[Unset, str]):
        no_score_count_by_split (Union[Unset, ExecutionsResponseCriterionNoScoreCountBySplit]):
        output_format (Union[Unset, OutputFormat]):
        prompt_execution_by_split (Union[Unset, ExecutionsResponseCriterionPromptExecutionBySplit]):
    """

    benchmark_uid: int
    criteria_uid: int
    evaluator_type: str
    name: str
    state: str
    code_execution_uid: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    error_score_count_by_split: Union[
        Unset, "ExecutionsResponseCriterionErrorScoreCountBySplit"
    ] = UNSET
    filter_config: Union[Unset, str] = UNSET
    no_score_count_by_split: Union[
        Unset, "ExecutionsResponseCriterionNoScoreCountBySplit"
    ] = UNSET
    output_format: Union[Unset, "OutputFormat"] = UNSET
    prompt_execution_by_split: Union[
        Unset, "ExecutionsResponseCriterionPromptExecutionBySplit"
    ] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.executions_response_criterion_error_score_count_by_split import (
            ExecutionsResponseCriterionErrorScoreCountBySplit,  # noqa: F401
        )
        from ..models.executions_response_criterion_no_score_count_by_split import (
            ExecutionsResponseCriterionNoScoreCountBySplit,  # noqa: F401
        )
        from ..models.executions_response_criterion_prompt_execution_by_split import (
            ExecutionsResponseCriterionPromptExecutionBySplit,  # noqa: F401
        )
        from ..models.output_format import OutputFormat  # noqa: F401
        # fmt: on
        benchmark_uid = self.benchmark_uid
        criteria_uid = self.criteria_uid
        evaluator_type = self.evaluator_type
        name = self.name
        state = self.state
        code_execution_uid = self.code_execution_uid
        description = self.description
        error_score_count_by_split: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.error_score_count_by_split, Unset):
            error_score_count_by_split = self.error_score_count_by_split.to_dict()
        filter_config = self.filter_config
        no_score_count_by_split: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.no_score_count_by_split, Unset):
            no_score_count_by_split = self.no_score_count_by_split.to_dict()
        output_format: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.output_format, Unset):
            output_format = self.output_format.to_dict()
        prompt_execution_by_split: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prompt_execution_by_split, Unset):
            prompt_execution_by_split = self.prompt_execution_by_split.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_uid": benchmark_uid,
                "criteria_uid": criteria_uid,
                "evaluator_type": evaluator_type,
                "name": name,
                "state": state,
            }
        )
        if code_execution_uid is not UNSET:
            field_dict["code_execution_uid"] = code_execution_uid
        if description is not UNSET:
            field_dict["description"] = description
        if error_score_count_by_split is not UNSET:
            field_dict["error_score_count_by_split"] = error_score_count_by_split
        if filter_config is not UNSET:
            field_dict["filter_config"] = filter_config
        if no_score_count_by_split is not UNSET:
            field_dict["no_score_count_by_split"] = no_score_count_by_split
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if prompt_execution_by_split is not UNSET:
            field_dict["prompt_execution_by_split"] = prompt_execution_by_split

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.executions_response_criterion_error_score_count_by_split import (
            ExecutionsResponseCriterionErrorScoreCountBySplit,  # noqa: F401
        )
        from ..models.executions_response_criterion_no_score_count_by_split import (
            ExecutionsResponseCriterionNoScoreCountBySplit,  # noqa: F401
        )
        from ..models.executions_response_criterion_prompt_execution_by_split import (
            ExecutionsResponseCriterionPromptExecutionBySplit,  # noqa: F401
        )
        from ..models.output_format import OutputFormat  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark_uid = d.pop("benchmark_uid")

        criteria_uid = d.pop("criteria_uid")

        evaluator_type = d.pop("evaluator_type")

        name = d.pop("name")

        state = d.pop("state")

        _code_execution_uid = d.pop("code_execution_uid", UNSET)
        code_execution_uid = (
            UNSET if _code_execution_uid is None else _code_execution_uid
        )

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _error_score_count_by_split = d.pop("error_score_count_by_split", UNSET)
        _error_score_count_by_split = (
            UNSET
            if _error_score_count_by_split is None
            else _error_score_count_by_split
        )
        error_score_count_by_split: Union[
            Unset, ExecutionsResponseCriterionErrorScoreCountBySplit
        ]
        if isinstance(_error_score_count_by_split, Unset):
            error_score_count_by_split = UNSET
        else:
            error_score_count_by_split = (
                ExecutionsResponseCriterionErrorScoreCountBySplit.from_dict(
                    _error_score_count_by_split
                )
            )

        _filter_config = d.pop("filter_config", UNSET)
        filter_config = UNSET if _filter_config is None else _filter_config

        _no_score_count_by_split = d.pop("no_score_count_by_split", UNSET)
        _no_score_count_by_split = (
            UNSET if _no_score_count_by_split is None else _no_score_count_by_split
        )
        no_score_count_by_split: Union[
            Unset, ExecutionsResponseCriterionNoScoreCountBySplit
        ]
        if isinstance(_no_score_count_by_split, Unset):
            no_score_count_by_split = UNSET
        else:
            no_score_count_by_split = (
                ExecutionsResponseCriterionNoScoreCountBySplit.from_dict(
                    _no_score_count_by_split
                )
            )

        _output_format = d.pop("output_format", UNSET)
        _output_format = UNSET if _output_format is None else _output_format
        output_format: Union[Unset, OutputFormat]
        if isinstance(_output_format, Unset):
            output_format = UNSET
        else:
            output_format = OutputFormat.from_dict(_output_format)

        _prompt_execution_by_split = d.pop("prompt_execution_by_split", UNSET)
        _prompt_execution_by_split = (
            UNSET if _prompt_execution_by_split is None else _prompt_execution_by_split
        )
        prompt_execution_by_split: Union[
            Unset, ExecutionsResponseCriterionPromptExecutionBySplit
        ]
        if isinstance(_prompt_execution_by_split, Unset):
            prompt_execution_by_split = UNSET
        else:
            prompt_execution_by_split = (
                ExecutionsResponseCriterionPromptExecutionBySplit.from_dict(
                    _prompt_execution_by_split
                )
            )

        obj = cls(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            evaluator_type=evaluator_type,
            name=name,
            state=state,
            code_execution_uid=code_execution_uid,
            description=description,
            error_score_count_by_split=error_score_count_by_split,
            filter_config=filter_config,
            no_score_count_by_split=no_score_count_by_split,
            output_format=output_format,
            prompt_execution_by_split=prompt_execution_by_split,
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
