from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.llmaj_response_score_label_ordinality import (
        LLMAJResponseScoreLabelOrdinality,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="LLMAJResponseScore")


@attrs.define
class LLMAJResponseScore:
    """
    Attributes:
        label (int):
        label_ordinality (LLMAJResponseScoreLabelOrdinality):
        label_schema_uid (int):
    """

    label: int
    label_ordinality: "LLMAJResponseScoreLabelOrdinality"
    label_schema_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.llmaj_response_score_label_ordinality import (
            LLMAJResponseScoreLabelOrdinality,  # noqa: F401
        )
        # fmt: on
        label = self.label
        label_ordinality = self.label_ordinality.to_dict()
        label_schema_uid = self.label_schema_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "label_ordinality": label_ordinality,
                "label_schema_uid": label_schema_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.llmaj_response_score_label_ordinality import (
            LLMAJResponseScoreLabelOrdinality,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        label = d.pop("label")

        label_ordinality = LLMAJResponseScoreLabelOrdinality.from_dict(
            d.pop("label_ordinality")
        )

        label_schema_uid = d.pop("label_schema_uid")

        obj = cls(
            label=label,
            label_ordinality=label_ordinality,
            label_schema_uid=label_schema_uid,
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
