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

T = TypeVar("T", bound="ApplyBenchmarkPopulatorRequest")


@attrs.define
class ApplyBenchmarkPopulatorRequest:
    """Request model for applying a benchmark populator.

    Attributes:
        benchmark_name (str):
        dataset_name (str):
        populator_directory_name (str):
        workspace_uid (int):
        user_uid (Union[Unset, int]):
    """

    benchmark_name: str
    dataset_name: str
    populator_directory_name: str
    workspace_uid: int
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        benchmark_name = self.benchmark_name
        dataset_name = self.dataset_name
        populator_directory_name = self.populator_directory_name
        workspace_uid = self.workspace_uid
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_name": benchmark_name,
                "dataset_name": dataset_name,
                "populator_directory_name": populator_directory_name,
                "workspace_uid": workspace_uid,
            }
        )
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        benchmark_name = d.pop("benchmark_name")

        dataset_name = d.pop("dataset_name")

        populator_directory_name = d.pop("populator_directory_name")

        workspace_uid = d.pop("workspace_uid")

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            benchmark_name=benchmark_name,
            dataset_name=dataset_name,
            populator_directory_name=populator_directory_name,
            workspace_uid=workspace_uid,
            user_uid=user_uid,
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
