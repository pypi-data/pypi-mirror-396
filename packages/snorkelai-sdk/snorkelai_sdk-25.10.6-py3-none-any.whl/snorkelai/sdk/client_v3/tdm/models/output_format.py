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

T = TypeVar("T", bound="OutputFormat")


@attrs.define
class OutputFormat:
    """
    Attributes:
        metric_label_schema_uid (int):
        rationale_label_schema_uid (Union[Unset, int]):
    """

    metric_label_schema_uid: int
    rationale_label_schema_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metric_label_schema_uid = self.metric_label_schema_uid
        rationale_label_schema_uid = self.rationale_label_schema_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric_label_schema_uid": metric_label_schema_uid,
            }
        )
        if rationale_label_schema_uid is not UNSET:
            field_dict["rationale_label_schema_uid"] = rationale_label_schema_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        metric_label_schema_uid = d.pop("metric_label_schema_uid")

        _rationale_label_schema_uid = d.pop("rationale_label_schema_uid", UNSET)
        rationale_label_schema_uid = (
            UNSET
            if _rationale_label_schema_uid is None
            else _rationale_label_schema_uid
        )

        obj = cls(
            metric_label_schema_uid=metric_label_schema_uid,
            rationale_label_schema_uid=rationale_label_schema_uid,
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
