from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="IndividualAnnotatorStatistics")


@attrs.define
class IndividualAnnotatorStatistics:
    """
    Attributes:
        annotation_count (int):
        annotation_target (int):
        source_uid (int):
        user_name (str):
        user_uid (int):
    """

    annotation_count: int
    annotation_target: int
    source_uid: int
    user_name: str
    user_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_count = self.annotation_count
        annotation_target = self.annotation_target
        source_uid = self.source_uid
        user_name = self.user_name
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_count": annotation_count,
                "annotation_target": annotation_target,
                "source_uid": source_uid,
                "user_name": user_name,
                "user_uid": user_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_count = d.pop("annotation_count")

        annotation_target = d.pop("annotation_target")

        source_uid = d.pop("source_uid")

        user_name = d.pop("user_name")

        user_uid = d.pop("user_uid")

        obj = cls(
            annotation_count=annotation_count,
            annotation_target=annotation_target,
            source_uid=source_uid,
            user_name=user_name,
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
