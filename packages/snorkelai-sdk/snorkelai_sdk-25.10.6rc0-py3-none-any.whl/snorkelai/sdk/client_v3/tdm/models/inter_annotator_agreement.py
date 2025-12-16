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

T = TypeVar("T", bound="InterAnnotatorAgreement")


@attrs.define
class InterAnnotatorAgreement:
    """
    Attributes:
        matrix (List[List[float]]):
        usernames (List[str]):
        metric (Union[Unset, float]):
    """

    matrix: List[List[float]]
    usernames: List[str]
    metric: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        matrix = []
        for matrix_item_data in self.matrix:
            matrix_item = matrix_item_data

            matrix.append(matrix_item)

        usernames = self.usernames

        metric = self.metric

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "matrix": matrix,
                "usernames": usernames,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        matrix = []
        _matrix = d.pop("matrix")
        for matrix_item_data in _matrix:
            matrix_item = cast(List[float], matrix_item_data)

            matrix.append(matrix_item)

        usernames = cast(List[str], d.pop("usernames"))

        _metric = d.pop("metric", UNSET)
        metric = UNSET if _metric is None else _metric

        obj = cls(
            matrix=matrix,
            usernames=usernames,
            metric=metric,
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
