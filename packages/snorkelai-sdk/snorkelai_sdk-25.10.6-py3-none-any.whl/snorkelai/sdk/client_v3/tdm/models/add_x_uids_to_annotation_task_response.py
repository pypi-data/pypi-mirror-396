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

T = TypeVar("T", bound="AddXUidsToAnnotationTaskResponse")


@attrs.define
class AddXUidsToAnnotationTaskResponse:
    """
    Attributes:
        added_x_uids (Union[Unset, List[str]]):
        failed_x_uids (Union[Unset, List[str]]):
    """

    added_x_uids: Union[Unset, List[str]] = UNSET
    failed_x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        added_x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.added_x_uids, Unset):
            added_x_uids = self.added_x_uids

        failed_x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.failed_x_uids, Unset):
            failed_x_uids = self.failed_x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if added_x_uids is not UNSET:
            field_dict["added_x_uids"] = added_x_uids
        if failed_x_uids is not UNSET:
            field_dict["failed_x_uids"] = failed_x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _added_x_uids = d.pop("added_x_uids", UNSET)
        added_x_uids = cast(
            List[str], UNSET if _added_x_uids is None else _added_x_uids
        )

        _failed_x_uids = d.pop("failed_x_uids", UNSET)
        failed_x_uids = cast(
            List[str], UNSET if _failed_x_uids is None else _failed_x_uids
        )

        obj = cls(
            added_x_uids=added_x_uids,
            failed_x_uids=failed_x_uids,
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
