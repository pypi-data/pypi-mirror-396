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

T = TypeVar("T", bound="DatasetCommentResponse")


@attrs.define
class DatasetCommentResponse:
    """
    Attributes:
        body (str):
        comment_uid (int):
        created_at (datetime.datetime):
        created_by_username (str):
        dataset_uid (int):
        user_uid (int):
        x_uid (str):
        is_edited (Union[Unset, bool]):  Default: False.
    """

    body: str
    comment_uid: int
    created_at: datetime.datetime
    created_by_username: str
    dataset_uid: int
    user_uid: int
    x_uid: str
    is_edited: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        body = self.body
        comment_uid = self.comment_uid
        created_at = self.created_at.isoformat()
        created_by_username = self.created_by_username
        dataset_uid = self.dataset_uid
        user_uid = self.user_uid
        x_uid = self.x_uid
        is_edited = self.is_edited

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
                "comment_uid": comment_uid,
                "created_at": created_at,
                "created_by_username": created_by_username,
                "dataset_uid": dataset_uid,
                "user_uid": user_uid,
                "x_uid": x_uid,
            }
        )
        if is_edited is not UNSET:
            field_dict["is_edited"] = is_edited

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        body = d.pop("body")

        comment_uid = d.pop("comment_uid")

        created_at = isoparse(d.pop("created_at"))

        created_by_username = d.pop("created_by_username")

        dataset_uid = d.pop("dataset_uid")

        user_uid = d.pop("user_uid")

        x_uid = d.pop("x_uid")

        _is_edited = d.pop("is_edited", UNSET)
        is_edited = UNSET if _is_edited is None else _is_edited

        obj = cls(
            body=body,
            comment_uid=comment_uid,
            created_at=created_at,
            created_by_username=created_by_username,
            dataset_uid=dataset_uid,
            user_uid=user_uid,
            x_uid=x_uid,
            is_edited=is_edited,
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
