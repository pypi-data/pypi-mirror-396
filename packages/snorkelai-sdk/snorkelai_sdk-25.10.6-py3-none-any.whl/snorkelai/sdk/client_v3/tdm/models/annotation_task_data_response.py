import datetime
from typing import (
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

T = TypeVar("T", bound="AnnotationTaskDataResponse")


@attrs.define
class AnnotationTaskDataResponse:
    """Response model with annotation task details and summarized counts.

    Attributes:
        annotation_task_uid (int):
        created_at (datetime.datetime):
        created_by_user_uid (int):
        datapoints_assigned_count (int):
        dataset_uid (int):
        label_forms_count (int):
        name (str):
        total_datapoints_count (int):
        users_assigned_count (int):
        description (Union[Unset, str]):
    """

    annotation_task_uid: int
    created_at: datetime.datetime
    created_by_user_uid: int
    datapoints_assigned_count: int
    dataset_uid: int
    label_forms_count: int
    name: str
    total_datapoints_count: int
    users_assigned_count: int
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_task_uid = self.annotation_task_uid
        created_at = self.created_at.isoformat()
        created_by_user_uid = self.created_by_user_uid
        datapoints_assigned_count = self.datapoints_assigned_count
        dataset_uid = self.dataset_uid
        label_forms_count = self.label_forms_count
        name = self.name
        total_datapoints_count = self.total_datapoints_count
        users_assigned_count = self.users_assigned_count
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_task_uid": annotation_task_uid,
                "created_at": created_at,
                "created_by_user_uid": created_by_user_uid,
                "datapoints_assigned_count": datapoints_assigned_count,
                "dataset_uid": dataset_uid,
                "label_forms_count": label_forms_count,
                "name": name,
                "total_datapoints_count": total_datapoints_count,
                "users_assigned_count": users_assigned_count,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_task_uid = d.pop("annotation_task_uid")

        created_at = isoparse(d.pop("created_at"))

        created_by_user_uid = d.pop("created_by_user_uid")

        datapoints_assigned_count = d.pop("datapoints_assigned_count")

        dataset_uid = d.pop("dataset_uid")

        label_forms_count = d.pop("label_forms_count")

        name = d.pop("name")

        total_datapoints_count = d.pop("total_datapoints_count")

        users_assigned_count = d.pop("users_assigned_count")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        obj = cls(
            annotation_task_uid=annotation_task_uid,
            created_at=created_at,
            created_by_user_uid=created_by_user_uid,
            datapoints_assigned_count=datapoints_assigned_count,
            dataset_uid=dataset_uid,
            label_forms_count=label_forms_count,
            name=name,
            total_datapoints_count=total_datapoints_count,
            users_assigned_count=users_assigned_count,
            description=description,
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
