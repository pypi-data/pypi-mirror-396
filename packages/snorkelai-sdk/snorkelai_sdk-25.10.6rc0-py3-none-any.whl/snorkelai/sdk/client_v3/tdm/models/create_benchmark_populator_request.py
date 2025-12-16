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

T = TypeVar("T", bound="CreateBenchmarkPopulatorRequest")


@attrs.define
class CreateBenchmarkPopulatorRequest:
    """Request model for creating a benchmark populator.

    This inherits from the job parameter model for creating a benchmark populator
    so we can add additional route-specific fields as needed.

    Currently, the route only pipes the request arguments to the job directly.
    We can refactor this inheritance relationship if the models need to diverge.

        Attributes:
            benchmark_uid (int):
            populator_description (str):
            populator_name (str):
            user_uid (Union[Unset, int]):
    """

    benchmark_uid: int
    populator_description: str
    populator_name: str
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        benchmark_uid = self.benchmark_uid
        populator_description = self.populator_description
        populator_name = self.populator_name
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_uid": benchmark_uid,
                "populator_description": populator_description,
                "populator_name": populator_name,
            }
        )
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        benchmark_uid = d.pop("benchmark_uid")

        populator_description = d.pop("populator_description")

        populator_name = d.pop("populator_name")

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            benchmark_uid=benchmark_uid,
            populator_description=populator_description,
            populator_name=populator_name,
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
