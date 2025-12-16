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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_task_assigned_work_status_response import (
        AnnotationTaskAssignedWorkStatusResponse,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AnnotationTaskAssignedWorkResponse")


@attrs.define
class AnnotationTaskAssignedWorkResponse:
    """Response model for user's annotation task work with progress information.

    Attributes:
        annotation_task_uid (int):
        dataset_uid (int):
        date_assigned (datetime.datetime):
        name (str):
        description (Union[Unset, str]):
        status (Union[Unset, AnnotationTaskAssignedWorkStatusResponse]):
    """

    annotation_task_uid: int
    dataset_uid: int
    date_assigned: datetime.datetime
    name: str
    description: Union[Unset, str] = UNSET
    status: Union[Unset, "AnnotationTaskAssignedWorkStatusResponse"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_task_assigned_work_status_response import (
            AnnotationTaskAssignedWorkStatusResponse,  # noqa: F401
        )
        # fmt: on
        annotation_task_uid = self.annotation_task_uid
        dataset_uid = self.dataset_uid
        date_assigned = self.date_assigned.isoformat()
        name = self.name
        description = self.description
        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_task_uid": annotation_task_uid,
                "dataset_uid": dataset_uid,
                "date_assigned": date_assigned,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_task_assigned_work_status_response import (
            AnnotationTaskAssignedWorkStatusResponse,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotation_task_uid = d.pop("annotation_task_uid")

        dataset_uid = d.pop("dataset_uid")

        date_assigned = isoparse(d.pop("date_assigned"))

        name = d.pop("name")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _status = d.pop("status", UNSET)
        _status = UNSET if _status is None else _status
        status: Union[Unset, AnnotationTaskAssignedWorkStatusResponse]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = AnnotationTaskAssignedWorkStatusResponse.from_dict(_status)

        obj = cls(
            annotation_task_uid=annotation_task_uid,
            dataset_uid=dataset_uid,
            date_assigned=date_assigned,
            name=name,
            description=description,
            status=status,
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
