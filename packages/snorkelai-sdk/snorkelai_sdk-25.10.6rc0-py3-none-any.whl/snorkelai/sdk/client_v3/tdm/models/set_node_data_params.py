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

T = TypeVar("T", bound="SetNodeDataParams")


@attrs.define
class SetNodeDataParams:
    """
    Attributes:
        datasource_uids_to_load (Union[Unset, List[int]]):
        enable_caching (Union[Unset, bool]):  Default: True.
        scheduler (Union[Unset, str]):
    """

    datasource_uids_to_load: Union[Unset, List[int]] = UNSET
    enable_caching: Union[Unset, bool] = True
    scheduler: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        datasource_uids_to_load: Union[Unset, List[int]] = UNSET
        if not isinstance(self.datasource_uids_to_load, Unset):
            datasource_uids_to_load = self.datasource_uids_to_load

        enable_caching = self.enable_caching
        scheduler = self.scheduler

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if datasource_uids_to_load is not UNSET:
            field_dict["datasource_uids_to_load"] = datasource_uids_to_load
        if enable_caching is not UNSET:
            field_dict["enable_caching"] = enable_caching
        if scheduler is not UNSET:
            field_dict["scheduler"] = scheduler

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _datasource_uids_to_load = d.pop("datasource_uids_to_load", UNSET)
        datasource_uids_to_load = cast(
            List[int],
            UNSET if _datasource_uids_to_load is None else _datasource_uids_to_load,
        )

        _enable_caching = d.pop("enable_caching", UNSET)
        enable_caching = UNSET if _enable_caching is None else _enable_caching

        _scheduler = d.pop("scheduler", UNSET)
        scheduler = UNSET if _scheduler is None else _scheduler

        obj = cls(
            datasource_uids_to_load=datasource_uids_to_load,
            enable_caching=enable_caching,
            scheduler=scheduler,
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
