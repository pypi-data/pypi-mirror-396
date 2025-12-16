from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.membership import Membership
from ..types import UNSET, Unset

T = TypeVar("T", bound="SliceMembershipInfo")


@attrs.define
class SliceMembershipInfo:
    """
    Attributes:
        slice_name (str):
        slice_uid (int):
        override (Union[Unset, Membership]):
        programmatic (Union[Unset, Membership]):
    """

    slice_name: str
    slice_uid: int
    override: Union[Unset, Membership] = UNSET
    programmatic: Union[Unset, Membership] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        slice_name = self.slice_name
        slice_uid = self.slice_uid
        override: Union[Unset, str] = UNSET
        if not isinstance(self.override, Unset):
            override = self.override.value

        programmatic: Union[Unset, str] = UNSET
        if not isinstance(self.programmatic, Unset):
            programmatic = self.programmatic.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slice_name": slice_name,
                "slice_uid": slice_uid,
            }
        )
        if override is not UNSET:
            field_dict["override"] = override
        if programmatic is not UNSET:
            field_dict["programmatic"] = programmatic

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        slice_name = d.pop("slice_name")

        slice_uid = d.pop("slice_uid")

        _override = d.pop("override", UNSET)
        _override = UNSET if _override is None else _override
        override: Union[Unset, Membership]
        if isinstance(_override, Unset):
            override = UNSET
        else:
            override = Membership(_override)

        _programmatic = d.pop("programmatic", UNSET)
        _programmatic = UNSET if _programmatic is None else _programmatic
        programmatic: Union[Unset, Membership]
        if isinstance(_programmatic, Unset):
            programmatic = UNSET
        else:
            programmatic = Membership(_programmatic)

        obj = cls(
            slice_name=slice_name,
            slice_uid=slice_uid,
            override=override,
            programmatic=programmatic,
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
