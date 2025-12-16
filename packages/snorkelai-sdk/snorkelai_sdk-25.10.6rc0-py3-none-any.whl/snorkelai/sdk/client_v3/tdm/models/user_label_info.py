from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserLabelInfo")


@attrs.define
class UserLabelInfo:
    """
    Attributes:
        user_uid (int):
        username (str):
        sequence_tag_spans (Union[Unset, List[Any]]):
    """

    user_uid: int
    username: str
    sequence_tag_spans: Union[Unset, List[Any]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_uid = self.user_uid
        username = self.username
        sequence_tag_spans: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.sequence_tag_spans, Unset):
            sequence_tag_spans = self.sequence_tag_spans

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_uid": user_uid,
                "username": username,
            }
        )
        if sequence_tag_spans is not UNSET:
            field_dict["sequence_tag_spans"] = sequence_tag_spans

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_uid = d.pop("user_uid")

        username = d.pop("username")

        _sequence_tag_spans = d.pop("sequence_tag_spans", UNSET)
        sequence_tag_spans = cast(
            List[Any], UNSET if _sequence_tag_spans is None else _sequence_tag_spans
        )

        obj = cls(
            user_uid=user_uid,
            username=username,
            sequence_tag_spans=sequence_tag_spans,
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
