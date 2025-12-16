import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_form import AnnotationForm  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnnotationTask")


@attrs.define
class AnnotationTask:
    """
    Attributes:
        annotation_form (AnnotationForm):
        annotation_task_uid (int):
        created_at (datetime.datetime):
        created_by_user_uid (int):
        dataset_uid (int):
        name (str):
        allow_auto_commit (Union[Unset, bool]):  Default: False.
        allow_reassignment (Union[Unset, bool]):  Default: False.
        description (Union[Unset, str]):
        entity_origin_uid (Union[Unset, int]):
        num_required_submission (Union[Unset, int]):
        user_visibility (Union[Unset, List[int]]):
        x_uids (Union[Unset, List[str]]):
    """

    annotation_form: "AnnotationForm"
    annotation_task_uid: int
    created_at: datetime.datetime
    created_by_user_uid: int
    dataset_uid: int
    name: str
    allow_auto_commit: Union[Unset, bool] = False
    allow_reassignment: Union[Unset, bool] = False
    description: Union[Unset, str] = UNSET
    entity_origin_uid: Union[Unset, int] = UNSET
    num_required_submission: Union[Unset, int] = UNSET
    user_visibility: Union[Unset, List[int]] = UNSET
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        # fmt: on
        annotation_form = self.annotation_form.to_dict()
        annotation_task_uid = self.annotation_task_uid
        created_at = self.created_at.isoformat()
        created_by_user_uid = self.created_by_user_uid
        dataset_uid = self.dataset_uid
        name = self.name
        allow_auto_commit = self.allow_auto_commit
        allow_reassignment = self.allow_reassignment
        description = self.description
        entity_origin_uid = self.entity_origin_uid
        num_required_submission = self.num_required_submission
        user_visibility: Union[Unset, List[int]] = UNSET
        if not isinstance(self.user_visibility, Unset):
            user_visibility = self.user_visibility

        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_form": annotation_form,
                "annotation_task_uid": annotation_task_uid,
                "created_at": created_at,
                "created_by_user_uid": created_by_user_uid,
                "dataset_uid": dataset_uid,
                "name": name,
            }
        )
        if allow_auto_commit is not UNSET:
            field_dict["allow_auto_commit"] = allow_auto_commit
        if allow_reassignment is not UNSET:
            field_dict["allow_reassignment"] = allow_reassignment
        if description is not UNSET:
            field_dict["description"] = description
        if entity_origin_uid is not UNSET:
            field_dict["entity_origin_uid"] = entity_origin_uid
        if num_required_submission is not UNSET:
            field_dict["num_required_submission"] = num_required_submission
        if user_visibility is not UNSET:
            field_dict["user_visibility"] = user_visibility
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotation_form = AnnotationForm.from_dict(d.pop("annotation_form"))

        annotation_task_uid = d.pop("annotation_task_uid")

        created_at = isoparse(d.pop("created_at"))

        created_by_user_uid = d.pop("created_by_user_uid")

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        _allow_auto_commit = d.pop("allow_auto_commit", UNSET)
        allow_auto_commit = UNSET if _allow_auto_commit is None else _allow_auto_commit

        _allow_reassignment = d.pop("allow_reassignment", UNSET)
        allow_reassignment = (
            UNSET if _allow_reassignment is None else _allow_reassignment
        )

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _entity_origin_uid = d.pop("entity_origin_uid", UNSET)
        entity_origin_uid = UNSET if _entity_origin_uid is None else _entity_origin_uid

        _num_required_submission = d.pop("num_required_submission", UNSET)
        num_required_submission = (
            UNSET if _num_required_submission is None else _num_required_submission
        )

        _user_visibility = d.pop("user_visibility", UNSET)
        user_visibility = cast(
            List[int], UNSET if _user_visibility is None else _user_visibility
        )

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            annotation_form=annotation_form,
            annotation_task_uid=annotation_task_uid,
            created_at=created_at,
            created_by_user_uid=created_by_user_uid,
            dataset_uid=dataset_uid,
            name=name,
            allow_auto_commit=allow_auto_commit,
            allow_reassignment=allow_reassignment,
            description=description,
            entity_origin_uid=entity_origin_uid,
            num_required_submission=num_required_submission,
            user_visibility=user_visibility,
            x_uids=x_uids,
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
