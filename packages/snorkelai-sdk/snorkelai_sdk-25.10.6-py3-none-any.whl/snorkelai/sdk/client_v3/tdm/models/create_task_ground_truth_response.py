from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateTaskGroundTruthResponse")


@attrs.define
class CreateTaskGroundTruthResponse:
    """
    Attributes:
        n_labels (int):
        task (int):
        warning (str):
        job (Union[Unset, str]):
    """

    n_labels: int
    task: int
    warning: str
    job: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        n_labels = self.n_labels
        task = self.task
        warning = self.warning
        job = self.job

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "n_labels": n_labels,
                "task": task,
                "warning": warning,
            }
        )
        if job is not UNSET:
            field_dict["job"] = job

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        n_labels = d.pop("n_labels")

        task = d.pop("task")

        warning = d.pop("warning")

        _job = d.pop("job", UNSET)
        job = UNSET if _job is None else _job

        obj = cls(
            n_labels=n_labels,
            task=task,
            warning=warning,
            job=job,
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
