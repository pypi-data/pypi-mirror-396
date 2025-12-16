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

T = TypeVar("T", bound="DeleteUserSettingsRequest")


@attrs.define
class DeleteUserSettingsRequest:
    """
    Attributes:
        dataset_batch_uid (Union[Unset, int]):
        node_uid (Union[Unset, int]):
        user_uid (Union[Unset, int]):
    """

    dataset_batch_uid: Union[Unset, int] = UNSET
    node_uid: Union[Unset, int] = UNSET
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_batch_uid = self.dataset_batch_uid
        node_uid = self.node_uid
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dataset_batch_uid is not UNSET:
            field_dict["dataset_batch_uid"] = dataset_batch_uid
        if node_uid is not UNSET:
            field_dict["node_uid"] = node_uid
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _dataset_batch_uid = d.pop("dataset_batch_uid", UNSET)
        dataset_batch_uid = UNSET if _dataset_batch_uid is None else _dataset_batch_uid

        _node_uid = d.pop("node_uid", UNSET)
        node_uid = UNSET if _node_uid is None else _node_uid

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            dataset_batch_uid=dataset_batch_uid,
            node_uid=node_uid,
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
