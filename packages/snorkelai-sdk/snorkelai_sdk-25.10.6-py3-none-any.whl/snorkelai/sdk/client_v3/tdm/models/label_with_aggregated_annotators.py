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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.user_label_info import UserLabelInfo  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LabelWithAggregatedAnnotators")


@attrs.define
class LabelWithAggregatedAnnotators:
    """
    Attributes:
        label_int (int):
        label_name (str):
        labeled_absent_users (Union[Unset, List['UserLabelInfo']]):
        labeled_by_users (Union[Unset, List['UserLabelInfo']]):
        labeled_present_users (Union[Unset, List['UserLabelInfo']]):
        labeled_unknown_users (Union[Unset, List['UserLabelInfo']]):
    """

    label_int: int
    label_name: str
    labeled_absent_users: Union[Unset, List["UserLabelInfo"]] = UNSET
    labeled_by_users: Union[Unset, List["UserLabelInfo"]] = UNSET
    labeled_present_users: Union[Unset, List["UserLabelInfo"]] = UNSET
    labeled_unknown_users: Union[Unset, List["UserLabelInfo"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.user_label_info import UserLabelInfo  # noqa: F401
        # fmt: on
        label_int = self.label_int
        label_name = self.label_name
        labeled_absent_users: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.labeled_absent_users, Unset):
            labeled_absent_users = []
            for labeled_absent_users_item_data in self.labeled_absent_users:
                labeled_absent_users_item = labeled_absent_users_item_data.to_dict()
                labeled_absent_users.append(labeled_absent_users_item)

        labeled_by_users: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.labeled_by_users, Unset):
            labeled_by_users = []
            for labeled_by_users_item_data in self.labeled_by_users:
                labeled_by_users_item = labeled_by_users_item_data.to_dict()
                labeled_by_users.append(labeled_by_users_item)

        labeled_present_users: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.labeled_present_users, Unset):
            labeled_present_users = []
            for labeled_present_users_item_data in self.labeled_present_users:
                labeled_present_users_item = labeled_present_users_item_data.to_dict()
                labeled_present_users.append(labeled_present_users_item)

        labeled_unknown_users: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.labeled_unknown_users, Unset):
            labeled_unknown_users = []
            for labeled_unknown_users_item_data in self.labeled_unknown_users:
                labeled_unknown_users_item = labeled_unknown_users_item_data.to_dict()
                labeled_unknown_users.append(labeled_unknown_users_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_int": label_int,
                "label_name": label_name,
            }
        )
        if labeled_absent_users is not UNSET:
            field_dict["labeled_absent_users"] = labeled_absent_users
        if labeled_by_users is not UNSET:
            field_dict["labeled_by_users"] = labeled_by_users
        if labeled_present_users is not UNSET:
            field_dict["labeled_present_users"] = labeled_present_users
        if labeled_unknown_users is not UNSET:
            field_dict["labeled_unknown_users"] = labeled_unknown_users

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.user_label_info import UserLabelInfo  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        label_int = d.pop("label_int")

        label_name = d.pop("label_name")

        _labeled_absent_users = d.pop("labeled_absent_users", UNSET)
        labeled_absent_users = []
        _labeled_absent_users = (
            UNSET if _labeled_absent_users is None else _labeled_absent_users
        )
        for labeled_absent_users_item_data in _labeled_absent_users or []:
            labeled_absent_users_item = UserLabelInfo.from_dict(
                labeled_absent_users_item_data
            )

            labeled_absent_users.append(labeled_absent_users_item)

        _labeled_by_users = d.pop("labeled_by_users", UNSET)
        labeled_by_users = []
        _labeled_by_users = UNSET if _labeled_by_users is None else _labeled_by_users
        for labeled_by_users_item_data in _labeled_by_users or []:
            labeled_by_users_item = UserLabelInfo.from_dict(labeled_by_users_item_data)

            labeled_by_users.append(labeled_by_users_item)

        _labeled_present_users = d.pop("labeled_present_users", UNSET)
        labeled_present_users = []
        _labeled_present_users = (
            UNSET if _labeled_present_users is None else _labeled_present_users
        )
        for labeled_present_users_item_data in _labeled_present_users or []:
            labeled_present_users_item = UserLabelInfo.from_dict(
                labeled_present_users_item_data
            )

            labeled_present_users.append(labeled_present_users_item)

        _labeled_unknown_users = d.pop("labeled_unknown_users", UNSET)
        labeled_unknown_users = []
        _labeled_unknown_users = (
            UNSET if _labeled_unknown_users is None else _labeled_unknown_users
        )
        for labeled_unknown_users_item_data in _labeled_unknown_users or []:
            labeled_unknown_users_item = UserLabelInfo.from_dict(
                labeled_unknown_users_item_data
            )

            labeled_unknown_users.append(labeled_unknown_users_item)

        obj = cls(
            label_int=label_int,
            label_name=label_name,
            labeled_absent_users=labeled_absent_users,
            labeled_by_users=labeled_by_users,
            labeled_present_users=labeled_present_users,
            labeled_unknown_users=labeled_unknown_users,
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
