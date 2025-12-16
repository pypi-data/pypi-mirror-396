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

T = TypeVar("T", bound="AnnotatorOverviewStats")


@attrs.define
class AnnotatorOverviewStats:
    """
    Attributes:
        annotation_count (int):
        annotation_target (int):
        daily_rate (float):
        username (str):
        user_uid (Union[Unset, int]):
    """

    annotation_count: int
    annotation_target: int
    daily_rate: float
    username: str
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_count = self.annotation_count
        annotation_target = self.annotation_target
        daily_rate = self.daily_rate
        username = self.username
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_count": annotation_count,
                "annotation_target": annotation_target,
                "daily_rate": daily_rate,
                "username": username,
            }
        )
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_count = d.pop("annotation_count")

        annotation_target = d.pop("annotation_target")

        daily_rate = d.pop("daily_rate")

        username = d.pop("username")

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            annotation_count=annotation_count,
            annotation_target=annotation_target,
            daily_rate=daily_rate,
            username=username,
            user_uid=user_uid,
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
