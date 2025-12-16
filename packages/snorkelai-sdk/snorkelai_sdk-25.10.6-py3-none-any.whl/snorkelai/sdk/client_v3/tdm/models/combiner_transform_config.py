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

from ..models.combiner_operator import CombinerOperator
from ..types import UNSET, Unset

T = TypeVar("T", bound="CombinerTransformConfig")


@attrs.define
class CombinerTransformConfig:
    """
    Attributes:
        operator (CombinerOperator):
        other_dataset_ids (Union[Unset, List[int]]):
        transform_config_type (Union[Literal['dataset_combiner'], Unset]):  Default: 'dataset_combiner'.
    """

    operator: CombinerOperator
    other_dataset_ids: Union[Unset, List[int]] = UNSET
    transform_config_type: Union[Literal["dataset_combiner"], Unset] = (
        "dataset_combiner"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        operator = self.operator.value
        other_dataset_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.other_dataset_ids, Unset):
            other_dataset_ids = self.other_dataset_ids

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "operator": operator,
            }
        )
        if other_dataset_ids is not UNSET:
            field_dict["other_dataset_ids"] = other_dataset_ids
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        operator = CombinerOperator(d.pop("operator"))

        _other_dataset_ids = d.pop("other_dataset_ids", UNSET)
        other_dataset_ids = cast(
            List[int], UNSET if _other_dataset_ids is None else _other_dataset_ids
        )

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            operator=operator,
            other_dataset_ids=other_dataset_ids,
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
