from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="CreateDatasetCommentParams")


@attrs.define
class CreateDatasetCommentParams:
    """
    Attributes:
        body (str):
        dataset_uid (int):
        user_uid (int):
        x_uid (str):
    """

    body: str
    dataset_uid: int
    user_uid: int
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        body = self.body
        dataset_uid = self.dataset_uid
        user_uid = self.user_uid
        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "body": body,
                "dataset_uid": dataset_uid,
                "user_uid": user_uid,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        body = d.pop("body")

        dataset_uid = d.pop("dataset_uid")

        user_uid = d.pop("user_uid")

        x_uid = d.pop("x_uid")

        obj = cls(
            body=body,
            dataset_uid=dataset_uid,
            user_uid=user_uid,
            x_uid=x_uid,
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
