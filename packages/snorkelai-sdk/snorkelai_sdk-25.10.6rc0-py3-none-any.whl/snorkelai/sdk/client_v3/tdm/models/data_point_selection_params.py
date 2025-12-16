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

T = TypeVar("T", bound="DataPointSelectionParams")


@attrs.define
class DataPointSelectionParams:
    """
    Attributes:
        exclude_x_uids (Union[Unset, List[str]]):
        filter_config_str (Union[Unset, str]):
        include_x_uids (Union[Unset, List[str]]):
        is_select_all (Union[Unset, bool]):  Default: False.
    """

    exclude_x_uids: Union[Unset, List[str]] = UNSET
    filter_config_str: Union[Unset, str] = UNSET
    include_x_uids: Union[Unset, List[str]] = UNSET
    is_select_all: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        exclude_x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.exclude_x_uids, Unset):
            exclude_x_uids = self.exclude_x_uids

        filter_config_str = self.filter_config_str
        include_x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.include_x_uids, Unset):
            include_x_uids = self.include_x_uids

        is_select_all = self.is_select_all

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if exclude_x_uids is not UNSET:
            field_dict["exclude_x_uids"] = exclude_x_uids
        if filter_config_str is not UNSET:
            field_dict["filter_config_str"] = filter_config_str
        if include_x_uids is not UNSET:
            field_dict["include_x_uids"] = include_x_uids
        if is_select_all is not UNSET:
            field_dict["is_select_all"] = is_select_all

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _exclude_x_uids = d.pop("exclude_x_uids", UNSET)
        exclude_x_uids = cast(
            List[str], UNSET if _exclude_x_uids is None else _exclude_x_uids
        )

        _filter_config_str = d.pop("filter_config_str", UNSET)
        filter_config_str = UNSET if _filter_config_str is None else _filter_config_str

        _include_x_uids = d.pop("include_x_uids", UNSET)
        include_x_uids = cast(
            List[str], UNSET if _include_x_uids is None else _include_x_uids
        )

        _is_select_all = d.pop("is_select_all", UNSET)
        is_select_all = UNSET if _is_select_all is None else _is_select_all

        obj = cls(
            exclude_x_uids=exclude_x_uids,
            filter_config_str=filter_config_str,
            include_x_uids=include_x_uids,
            is_select_all=is_select_all,
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
