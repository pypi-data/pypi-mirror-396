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

T = TypeVar("T", bound="NotebookSettings")


@attrs.define
class NotebookSettings:
    """
    Attributes:
        version (int):
        export_enabled (Union[Unset, bool]):  Default: True.
        package_manager_enabled (Union[Unset, bool]):  Default: False.
        terminals_enabled (Union[Unset, bool]):  Default: False.
    """

    version: int
    export_enabled: Union[Unset, bool] = True
    package_manager_enabled: Union[Unset, bool] = False
    terminals_enabled: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        version = self.version
        export_enabled = self.export_enabled
        package_manager_enabled = self.package_manager_enabled
        terminals_enabled = self.terminals_enabled

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
            }
        )
        if export_enabled is not UNSET:
            field_dict["export_enabled"] = export_enabled
        if package_manager_enabled is not UNSET:
            field_dict["package_manager_enabled"] = package_manager_enabled
        if terminals_enabled is not UNSET:
            field_dict["terminals_enabled"] = terminals_enabled

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        version = d.pop("version")

        _export_enabled = d.pop("export_enabled", UNSET)
        export_enabled = UNSET if _export_enabled is None else _export_enabled

        _package_manager_enabled = d.pop("package_manager_enabled", UNSET)
        package_manager_enabled = (
            UNSET if _package_manager_enabled is None else _package_manager_enabled
        )

        _terminals_enabled = d.pop("terminals_enabled", UNSET)
        terminals_enabled = UNSET if _terminals_enabled is None else _terminals_enabled

        obj = cls(
            version=version,
            export_enabled=export_enabled,
            package_manager_enabled=package_manager_enabled,
            terminals_enabled=terminals_enabled,
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
