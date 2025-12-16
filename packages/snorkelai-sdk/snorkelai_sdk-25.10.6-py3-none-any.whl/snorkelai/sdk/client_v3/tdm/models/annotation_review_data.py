from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.annotation_review_state import AnnotationReviewState
from ..models.task_type import TaskType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotationReviewData")


@attrs.define
class AnnotationReviewData:
    """
    Attributes:
        label_schema_uid (int):
        raw_label (str):
        review_status (AnnotationReviewState):
        task_type (TaskType):
        user_uid (int):
        end (Union[Unset, int]):  Default: 0.
        start (Union[Unset, int]):  Default: 0.
    """

    label_schema_uid: int
    raw_label: str
    review_status: AnnotationReviewState
    task_type: TaskType
    user_uid: int
    end: Union[Unset, int] = 0
    start: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label_schema_uid = self.label_schema_uid
        raw_label = self.raw_label
        review_status = self.review_status.value
        task_type = self.task_type.value
        user_uid = self.user_uid
        end = self.end
        start = self.start

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_schema_uid": label_schema_uid,
                "raw_label": raw_label,
                "review_status": review_status,
                "task_type": task_type,
                "user_uid": user_uid,
            }
        )
        if end is not UNSET:
            field_dict["end"] = end
        if start is not UNSET:
            field_dict["start"] = start

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_schema_uid = d.pop("label_schema_uid")

        raw_label = d.pop("raw_label")

        review_status = AnnotationReviewState(d.pop("review_status"))

        task_type = TaskType(d.pop("task_type"))

        user_uid = d.pop("user_uid")

        _end = d.pop("end", UNSET)
        end = UNSET if _end is None else _end

        _start = d.pop("start", UNSET)
        start = UNSET if _start is None else _start

        obj = cls(
            label_schema_uid=label_schema_uid,
            raw_label=raw_label,
            review_status=review_status,
            task_type=task_type,
            user_uid=user_uid,
            end=end,
            start=start,
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
