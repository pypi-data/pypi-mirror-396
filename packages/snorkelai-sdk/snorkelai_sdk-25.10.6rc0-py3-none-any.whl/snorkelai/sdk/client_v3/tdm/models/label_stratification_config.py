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

T = TypeVar("T", bound="LabelStratificationConfig")


@attrs.define
class LabelStratificationConfig:
    """Parameters for ground truth stratification.

    Attributes:
        gt_col (Union[Unset, str]):
        unknown_gt_value (Union[Unset, Any]):
    """

    gt_col: Union[Unset, str] = UNSET
    unknown_gt_value: Union[Unset, Any] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        gt_col = self.gt_col
        unknown_gt_value = self.unknown_gt_value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gt_col is not UNSET:
            field_dict["gt_col"] = gt_col
        if unknown_gt_value is not UNSET:
            field_dict["unknown_gt_value"] = unknown_gt_value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _gt_col = d.pop("gt_col", UNSET)
        gt_col = UNSET if _gt_col is None else _gt_col

        _unknown_gt_value = d.pop("unknown_gt_value", UNSET)
        unknown_gt_value = UNSET if _unknown_gt_value is None else _unknown_gt_value

        obj = cls(
            gt_col=gt_col,
            unknown_gt_value=unknown_gt_value,
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
