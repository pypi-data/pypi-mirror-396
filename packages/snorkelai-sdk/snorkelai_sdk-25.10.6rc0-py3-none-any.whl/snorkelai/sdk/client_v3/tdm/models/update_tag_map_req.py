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

T = TypeVar("T", bound="UpdateTagMapReq")


@attrs.define
class UpdateTagMapReq:
    """
    Attributes:
        add_tag_type_uids (Union[Unset, List[int]]):
        remove_tag_type_uids (Union[Unset, List[int]]):
        skip_missing (Union[Unset, bool]):  Default: False.
        tag_type_uids (Union[Unset, List[int]]):
        x_uids (Union[Unset, List[str]]):
    """

    add_tag_type_uids: Union[Unset, List[int]] = UNSET
    remove_tag_type_uids: Union[Unset, List[int]] = UNSET
    skip_missing: Union[Unset, bool] = False
    tag_type_uids: Union[Unset, List[int]] = UNSET
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        add_tag_type_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.add_tag_type_uids, Unset):
            add_tag_type_uids = self.add_tag_type_uids

        remove_tag_type_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.remove_tag_type_uids, Unset):
            remove_tag_type_uids = self.remove_tag_type_uids

        skip_missing = self.skip_missing
        tag_type_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.tag_type_uids, Unset):
            tag_type_uids = self.tag_type_uids

        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if add_tag_type_uids is not UNSET:
            field_dict["add_tag_type_uids"] = add_tag_type_uids
        if remove_tag_type_uids is not UNSET:
            field_dict["remove_tag_type_uids"] = remove_tag_type_uids
        if skip_missing is not UNSET:
            field_dict["skip_missing"] = skip_missing
        if tag_type_uids is not UNSET:
            field_dict["tag_type_uids"] = tag_type_uids
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _add_tag_type_uids = d.pop("add_tag_type_uids", UNSET)
        add_tag_type_uids = cast(
            List[int], UNSET if _add_tag_type_uids is None else _add_tag_type_uids
        )

        _remove_tag_type_uids = d.pop("remove_tag_type_uids", UNSET)
        remove_tag_type_uids = cast(
            List[int], UNSET if _remove_tag_type_uids is None else _remove_tag_type_uids
        )

        _skip_missing = d.pop("skip_missing", UNSET)
        skip_missing = UNSET if _skip_missing is None else _skip_missing

        _tag_type_uids = d.pop("tag_type_uids", UNSET)
        tag_type_uids = cast(
            List[int], UNSET if _tag_type_uids is None else _tag_type_uids
        )

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            add_tag_type_uids=add_tag_type_uids,
            remove_tag_type_uids=remove_tag_type_uids,
            skip_missing=skip_missing,
            tag_type_uids=tag_type_uids,
            x_uids=x_uids,
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
