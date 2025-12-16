from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="VDSSorterConfig")


@attrs.define
class VDSSorterConfig:
    """Configuration for sorting VirtualizedDataset by one or more columns.

    Args:
        sort: List of column names to sort by (required).
        ascending: List of boolean values indicating sort order for each column.
                  If not provided, defaults to True for all columns.

        Attributes:
            sort (List[str]):
            ascending (Union[Unset, List[bool]]):
            transform_config_type (Union[Literal['vds_sorter'], Unset]):  Default: 'vds_sorter'.
    """

    sort: List[str]
    ascending: Union[Unset, List[bool]] = UNSET
    transform_config_type: Union[Literal["vds_sorter"], Unset] = "vds_sorter"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sort = self.sort

        ascending: Union[Unset, List[bool]] = UNSET
        if not isinstance(self.ascending, Unset):
            ascending = self.ascending

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sort": sort,
            }
        )
        if ascending is not UNSET:
            field_dict["ascending"] = ascending
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        sort = cast(List[str], d.pop("sort"))

        _ascending = d.pop("ascending", UNSET)
        ascending = cast(List[bool], UNSET if _ascending is None else _ascending)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            sort=sort,
            ascending=ascending,
            transform_config_type=transform_config_type,
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
