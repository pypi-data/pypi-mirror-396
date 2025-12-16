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

T = TypeVar("T", bound="ExecutionsResponseMetric")


@attrs.define
class ExecutionsResponseMetric:
    """Response model for individual metrics that includes value, error, and warning fields
    from EvaluationMetric.

        Attributes:
            error (Union[Unset, str]):
            value (Union[Unset, float]):
            warning (Union[Unset, str]):
    """

    error: Union[Unset, str] = UNSET
    value: Union[Unset, float] = UNSET
    warning: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        error = self.error
        value = self.value
        warning = self.warning

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error is not UNSET:
            field_dict["error"] = error
        if value is not UNSET:
            field_dict["value"] = value
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _error = d.pop("error", UNSET)
        error = UNSET if _error is None else _error

        _value = d.pop("value", UNSET)
        value = UNSET if _value is None else _value

        _warning = d.pop("warning", UNSET)
        warning = UNSET if _warning is None else _warning

        obj = cls(
            error=error,
            value=value,
            warning=warning,
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
