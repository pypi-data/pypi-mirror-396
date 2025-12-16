from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.input_warning import InputWarning  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="UniqueLabelsResponse")


@attrs.define
class UniqueLabelsResponse:
    """
    Attributes:
        label_counts (List[int]):
        labels (List[str]):
        warnings (List['InputWarning']):
    """

    label_counts: List[int]
    labels: List[str]
    warnings: List["InputWarning"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.input_warning import InputWarning  # noqa: F401
        # fmt: on
        label_counts = self.label_counts

        labels = self.labels

        warnings = []
        for warnings_item_data in self.warnings:
            warnings_item = warnings_item_data.to_dict()
            warnings.append(warnings_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_counts": label_counts,
                "labels": labels,
                "warnings": warnings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.input_warning import InputWarning  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        label_counts = cast(List[int], d.pop("label_counts"))

        labels = cast(List[str], d.pop("labels"))

        warnings = []
        _warnings = d.pop("warnings")
        for warnings_item_data in _warnings:
            warnings_item = InputWarning.from_dict(warnings_item_data)

            warnings.append(warnings_item)

        obj = cls(
            label_counts=label_counts,
            labels=labels,
            warnings=warnings,
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
