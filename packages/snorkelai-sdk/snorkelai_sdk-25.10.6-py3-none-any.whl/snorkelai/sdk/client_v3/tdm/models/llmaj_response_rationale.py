from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="LLMAJResponseRationale")


@attrs.define
class LLMAJResponseRationale:
    """
    Attributes:
        label_schema_uid (int):
        rationale (str):
    """

    label_schema_uid: int
    rationale: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label_schema_uid = self.label_schema_uid
        rationale = self.rationale

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_schema_uid": label_schema_uid,
                "rationale": rationale,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_schema_uid = d.pop("label_schema_uid")

        rationale = d.pop("rationale")

        obj = cls(
            label_schema_uid=label_schema_uid,
            rationale=rationale,
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
