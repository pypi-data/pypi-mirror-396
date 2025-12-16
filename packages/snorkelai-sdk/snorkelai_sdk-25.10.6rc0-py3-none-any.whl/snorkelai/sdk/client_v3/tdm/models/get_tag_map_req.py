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

T = TypeVar("T", bound="GetTagMapReq")


@attrs.define
class GetTagMapReq:
    """
    Attributes:
        exclude_tag_type_uids (Union[Unset, List[int]]):
        include_tag_type_uids (Union[Unset, List[int]]):
        is_context_tag_type (Union[Unset, bool]):
        limit (Union[Unset, int]):
        x_uids (Union[Unset, List[str]]):
    """

    exclude_tag_type_uids: Union[Unset, List[int]] = UNSET
    include_tag_type_uids: Union[Unset, List[int]] = UNSET
    is_context_tag_type: Union[Unset, bool] = UNSET
    limit: Union[Unset, int] = UNSET
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        exclude_tag_type_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.exclude_tag_type_uids, Unset):
            exclude_tag_type_uids = self.exclude_tag_type_uids

        include_tag_type_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.include_tag_type_uids, Unset):
            include_tag_type_uids = self.include_tag_type_uids

        is_context_tag_type = self.is_context_tag_type
        limit = self.limit
        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if exclude_tag_type_uids is not UNSET:
            field_dict["exclude_tag_type_uids"] = exclude_tag_type_uids
        if include_tag_type_uids is not UNSET:
            field_dict["include_tag_type_uids"] = include_tag_type_uids
        if is_context_tag_type is not UNSET:
            field_dict["is_context_tag_type"] = is_context_tag_type
        if limit is not UNSET:
            field_dict["limit"] = limit
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _exclude_tag_type_uids = d.pop("exclude_tag_type_uids", UNSET)
        exclude_tag_type_uids = cast(
            List[int],
            UNSET if _exclude_tag_type_uids is None else _exclude_tag_type_uids,
        )

        _include_tag_type_uids = d.pop("include_tag_type_uids", UNSET)
        include_tag_type_uids = cast(
            List[int],
            UNSET if _include_tag_type_uids is None else _include_tag_type_uids,
        )

        _is_context_tag_type = d.pop("is_context_tag_type", UNSET)
        is_context_tag_type = (
            UNSET if _is_context_tag_type is None else _is_context_tag_type
        )

        _limit = d.pop("limit", UNSET)
        limit = UNSET if _limit is None else _limit

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            exclude_tag_type_uids=exclude_tag_type_uids,
            include_tag_type_uids=include_tag_type_uids,
            is_context_tag_type=is_context_tag_type,
            limit=limit,
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
