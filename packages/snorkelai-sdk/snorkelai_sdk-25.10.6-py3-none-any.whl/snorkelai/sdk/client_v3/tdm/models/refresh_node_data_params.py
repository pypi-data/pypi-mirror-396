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

T = TypeVar("T", bound="RefreshNodeDataParams")


@attrs.define
class RefreshNodeDataParams:
    """
    Attributes:
        enable_caching (Union[Unset, bool]):  Default: True.
        scheduler (Union[Unset, str]):
        skip_repartition (Union[Unset, bool]):
    """

    enable_caching: Union[Unset, bool] = True
    scheduler: Union[Unset, str] = UNSET
    skip_repartition: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        enable_caching = self.enable_caching
        scheduler = self.scheduler
        skip_repartition = self.skip_repartition

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_caching is not UNSET:
            field_dict["enable_caching"] = enable_caching
        if scheduler is not UNSET:
            field_dict["scheduler"] = scheduler
        if skip_repartition is not UNSET:
            field_dict["skip_repartition"] = skip_repartition

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _enable_caching = d.pop("enable_caching", UNSET)
        enable_caching = UNSET if _enable_caching is None else _enable_caching

        _scheduler = d.pop("scheduler", UNSET)
        scheduler = UNSET if _scheduler is None else _scheduler

        _skip_repartition = d.pop("skip_repartition", UNSET)
        skip_repartition = UNSET if _skip_repartition is None else _skip_repartition

        obj = cls(
            enable_caching=enable_caching,
            scheduler=scheduler,
            skip_repartition=skip_repartition,
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
