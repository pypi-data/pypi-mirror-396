from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="DatapointAssigneeParams")


@attrs.define
class DatapointAssigneeParams:
    """Assignment of users to a single datapoint.

    Attributes:
        assignee_user_uids (List[int]):
        x_uid (str):
    """

    assignee_user_uids: List[int]
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        assignee_user_uids = self.assignee_user_uids

        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assignee_user_uids": assignee_user_uids,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assignee_user_uids = cast(List[int], d.pop("assignee_user_uids"))

        x_uid = d.pop("x_uid")

        obj = cls(
            assignee_user_uids=assignee_user_uids,
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
