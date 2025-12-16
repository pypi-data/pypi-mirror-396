from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetBatchSorterConfig")


@attrs.define
class DatasetBatchSorterConfig:
    """
    Attributes:
        dataset_uid (int):
        ascending (Union[Unset, bool]):  Default: True.
        transform_config_type (Union[Literal['dataset_batch_sorter'], Unset]):  Default: 'dataset_batch_sorter'.
    """

    dataset_uid: int
    ascending: Union[Unset, bool] = True
    transform_config_type: Union[Literal["dataset_batch_sorter"], Unset] = (
        "dataset_batch_sorter"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_uid = self.dataset_uid
        ascending = self.ascending
        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
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
        dataset_uid = d.pop("dataset_uid")

        _ascending = d.pop("ascending", UNSET)
        ascending = UNSET if _ascending is None else _ascending

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            dataset_uid=dataset_uid,
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
