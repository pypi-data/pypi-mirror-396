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

T = TypeVar("T", bound="PrepAndIngestDatasourceRequest")


@attrs.define
class PrepAndIngestDatasourceRequest:
    """
    Attributes:
        paths (List[str]):
        input_type (Union[Unset, str]):  Default: 'image'.
        run_datasource_checks (Union[Unset, bool]):  Default: False.
        split (Union[Unset, str]):  Default: 'train'.
    """

    paths: List[str]
    input_type: Union[Unset, str] = "image"
    run_datasource_checks: Union[Unset, bool] = False
    split: Union[Unset, str] = "train"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        paths = self.paths

        input_type = self.input_type
        run_datasource_checks = self.run_datasource_checks
        split = self.split

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "paths": paths,
            }
        )
        if input_type is not UNSET:
            field_dict["input_type"] = input_type
        if run_datasource_checks is not UNSET:
            field_dict["run_datasource_checks"] = run_datasource_checks
        if split is not UNSET:
            field_dict["split"] = split

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        paths = cast(List[str], d.pop("paths"))

        _input_type = d.pop("input_type", UNSET)
        input_type = UNSET if _input_type is None else _input_type

        _run_datasource_checks = d.pop("run_datasource_checks", UNSET)
        run_datasource_checks = (
            UNSET if _run_datasource_checks is None else _run_datasource_checks
        )

        _split = d.pop("split", UNSET)
        split = UNSET if _split is None else _split

        obj = cls(
            paths=paths,
            input_type=input_type,
            run_datasource_checks=run_datasource_checks,
            split=split,
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
