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

from ..models.evaluator_type import EvaluatorType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.output_format import OutputFormat  # noqa: F401
    from ..models.prompt_evaluator_prompt_execution_uid_by_partition import (
        PromptEvaluatorPromptExecutionUidByPartition,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptEvaluator")


@attrs.define
class PromptEvaluator:
    """
    Attributes:
        criteria_uid (int):
        evaluator_uid (int):
        name (str):
        prompt_uid (int):
        prompt_workflow_uid (int):
        benchmark_uid (Union[Unset, int]):
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        output_format (Union[Unset, OutputFormat]):
        prompt_execution_uid_by_partition (Union[Unset, PromptEvaluatorPromptExecutionUidByPartition]):
        type (Union[Unset, EvaluatorType]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    criteria_uid: int
    evaluator_uid: int
    name: str
    prompt_uid: int
    prompt_workflow_uid: int
    benchmark_uid: Union[Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    output_format: Union[Unset, "OutputFormat"] = UNSET
    prompt_execution_uid_by_partition: Union[
        Unset, "PromptEvaluatorPromptExecutionUidByPartition"
    ] = UNSET
    type: Union[Unset, EvaluatorType] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.output_format import OutputFormat  # noqa: F401
        from ..models.prompt_evaluator_prompt_execution_uid_by_partition import (
            PromptEvaluatorPromptExecutionUidByPartition,  # noqa: F401
        )
        # fmt: on
        criteria_uid = self.criteria_uid
        evaluator_uid = self.evaluator_uid
        name = self.name
        prompt_uid = self.prompt_uid
        prompt_workflow_uid = self.prompt_workflow_uid
        benchmark_uid = self.benchmark_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description
        output_format: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.output_format, Unset):
            output_format = self.output_format.to_dict()
        prompt_execution_uid_by_partition: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prompt_execution_uid_by_partition, Unset):
            prompt_execution_uid_by_partition = (
                self.prompt_execution_uid_by_partition.to_dict()
            )
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_uid": criteria_uid,
                "evaluator_uid": evaluator_uid,
                "name": name,
                "prompt_uid": prompt_uid,
                "prompt_workflow_uid": prompt_workflow_uid,
            }
        )
        if benchmark_uid is not UNSET:
            field_dict["benchmark_uid"] = benchmark_uid
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if prompt_execution_uid_by_partition is not UNSET:
            field_dict["prompt_execution_uid_by_partition"] = (
                prompt_execution_uid_by_partition
            )
        if type is not UNSET:
            field_dict["type"] = type
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.output_format import OutputFormat  # noqa: F401
        from ..models.prompt_evaluator_prompt_execution_uid_by_partition import (
            PromptEvaluatorPromptExecutionUidByPartition,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        criteria_uid = d.pop("criteria_uid")

        evaluator_uid = d.pop("evaluator_uid")

        name = d.pop("name")

        prompt_uid = d.pop("prompt_uid")

        prompt_workflow_uid = d.pop("prompt_workflow_uid")

        _benchmark_uid = d.pop("benchmark_uid", UNSET)
        benchmark_uid = UNSET if _benchmark_uid is None else _benchmark_uid

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _output_format = d.pop("output_format", UNSET)
        _output_format = UNSET if _output_format is None else _output_format
        output_format: Union[Unset, OutputFormat]
        if isinstance(_output_format, Unset):
            output_format = UNSET
        else:
            output_format = OutputFormat.from_dict(_output_format)

        _prompt_execution_uid_by_partition = d.pop(
            "prompt_execution_uid_by_partition", UNSET
        )
        _prompt_execution_uid_by_partition = (
            UNSET
            if _prompt_execution_uid_by_partition is None
            else _prompt_execution_uid_by_partition
        )
        prompt_execution_uid_by_partition: Union[
            Unset, PromptEvaluatorPromptExecutionUidByPartition
        ]
        if isinstance(_prompt_execution_uid_by_partition, Unset):
            prompt_execution_uid_by_partition = UNSET
        else:
            prompt_execution_uid_by_partition = (
                PromptEvaluatorPromptExecutionUidByPartition.from_dict(
                    _prompt_execution_uid_by_partition
                )
            )

        _type = d.pop("type", UNSET)
        _type = UNSET if _type is None else _type
        type: Union[Unset, EvaluatorType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EvaluatorType(_type)

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            criteria_uid=criteria_uid,
            evaluator_uid=evaluator_uid,
            name=name,
            prompt_uid=prompt_uid,
            prompt_workflow_uid=prompt_workflow_uid,
            benchmark_uid=benchmark_uid,
            created_at=created_at,
            description=description,
            output_format=output_format,
            prompt_execution_uid_by_partition=prompt_execution_uid_by_partition,
            type=type,
            updated_at=updated_at,
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
