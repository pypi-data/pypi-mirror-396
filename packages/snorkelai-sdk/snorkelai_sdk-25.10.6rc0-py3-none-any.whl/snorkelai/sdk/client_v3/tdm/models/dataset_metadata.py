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

T = TypeVar("T", bound="DatasetMetadata")


@attrs.define
class DatasetMetadata:
    """
    Attributes:
        allow_generate_uid_col (Union[Unset, bool]):  Default: False.
        data_type (Union[Unset, str]):
        enable_mta (Union[Unset, bool]):  Default: False.
        num_datasources (Union[Unset, int]):  Default: 0.
    """

    allow_generate_uid_col: Union[Unset, bool] = False
    data_type: Union[Unset, str] = UNSET
    enable_mta: Union[Unset, bool] = False
    num_datasources: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_generate_uid_col = self.allow_generate_uid_col
        data_type = self.data_type
        enable_mta = self.enable_mta
        num_datasources = self.num_datasources

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allow_generate_uid_col is not UNSET:
            field_dict["allow_generate_uid_col"] = allow_generate_uid_col
        if data_type is not UNSET:
            field_dict["data_type"] = data_type
        if enable_mta is not UNSET:
            field_dict["enable_mta"] = enable_mta
        if num_datasources is not UNSET:
            field_dict["num_datasources"] = num_datasources

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _allow_generate_uid_col = d.pop("allow_generate_uid_col", UNSET)
        allow_generate_uid_col = (
            UNSET if _allow_generate_uid_col is None else _allow_generate_uid_col
        )

        _data_type = d.pop("data_type", UNSET)
        data_type = UNSET if _data_type is None else _data_type

        _enable_mta = d.pop("enable_mta", UNSET)
        enable_mta = UNSET if _enable_mta is None else _enable_mta

        _num_datasources = d.pop("num_datasources", UNSET)
        num_datasources = UNSET if _num_datasources is None else _num_datasources

        obj = cls(
            allow_generate_uid_col=allow_generate_uid_col,
            data_type=data_type,
            enable_mta=enable_mta,
            num_datasources=num_datasources,
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
