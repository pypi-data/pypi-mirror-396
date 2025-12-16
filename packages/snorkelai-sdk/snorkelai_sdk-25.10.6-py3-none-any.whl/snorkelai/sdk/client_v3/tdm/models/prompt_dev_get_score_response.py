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
    from ..models.evaluation_score_with_prompt_execution_uid import (
        EvaluationScoreWithPromptExecutionUid,  # noqa: F401
    )
    from ..models.prompt_dev_execution_job_status import (
        PromptDevExecutionJobStatus,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptDevGetScoreResponse")


@attrs.define
class PromptDevGetScoreResponse:
    """
    Attributes:
        execution_jobs (List['PromptDevExecutionJobStatus']):
        scores (List['EvaluationScoreWithPromptExecutionUid']):
    """

    execution_jobs: List["PromptDevExecutionJobStatus"]
    scores: List["EvaluationScoreWithPromptExecutionUid"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.evaluation_score_with_prompt_execution_uid import (
            EvaluationScoreWithPromptExecutionUid,  # noqa: F401
        )
        from ..models.prompt_dev_execution_job_status import (
            PromptDevExecutionJobStatus,  # noqa: F401
        )
        # fmt: on
        execution_jobs = []
        for execution_jobs_item_data in self.execution_jobs:
            execution_jobs_item = execution_jobs_item_data.to_dict()
            execution_jobs.append(execution_jobs_item)

        scores = []
        for scores_item_data in self.scores:
            scores_item = scores_item_data.to_dict()
            scores.append(scores_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_jobs": execution_jobs,
                "scores": scores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.evaluation_score_with_prompt_execution_uid import (
            EvaluationScoreWithPromptExecutionUid,  # noqa: F401
        )
        from ..models.prompt_dev_execution_job_status import (
            PromptDevExecutionJobStatus,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        execution_jobs = []
        _execution_jobs = d.pop("execution_jobs")
        for execution_jobs_item_data in _execution_jobs:
            execution_jobs_item = PromptDevExecutionJobStatus.from_dict(
                execution_jobs_item_data
            )

            execution_jobs.append(execution_jobs_item)

        scores = []
        _scores = d.pop("scores")
        for scores_item_data in _scores:
            scores_item = EvaluationScoreWithPromptExecutionUid.from_dict(
                scores_item_data
            )

            scores.append(scores_item)

        obj = cls(
            execution_jobs=execution_jobs,
            scores=scores,
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
