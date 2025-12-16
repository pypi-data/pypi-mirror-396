from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.label_type import LabelType

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_schema_annotator_summary_labels_annotators import (
        LabelSchemaAnnotatorSummaryLabelsAnnotators,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="LabelSchemaAnnotatorSummary")


@attrs.define
class LabelSchemaAnnotatorSummary:
    """
    Attributes:
        label_schema_uid (int):
        label_type (LabelType):
        labels_annotators (LabelSchemaAnnotatorSummaryLabelsAnnotators):
        name (str):
    """

    label_schema_uid: int
    label_type: LabelType
    labels_annotators: "LabelSchemaAnnotatorSummaryLabelsAnnotators"
    name: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_annotator_summary_labels_annotators import (
            LabelSchemaAnnotatorSummaryLabelsAnnotators,  # noqa: F401
        )
        # fmt: on
        label_schema_uid = self.label_schema_uid
        label_type = self.label_type.value
        labels_annotators = self.labels_annotators.to_dict()
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_schema_uid": label_schema_uid,
                "label_type": label_type,
                "labels_annotators": labels_annotators,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_annotator_summary_labels_annotators import (
            LabelSchemaAnnotatorSummaryLabelsAnnotators,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        label_schema_uid = d.pop("label_schema_uid")

        label_type = LabelType(d.pop("label_type"))

        labels_annotators = LabelSchemaAnnotatorSummaryLabelsAnnotators.from_dict(
            d.pop("labels_annotators")
        )

        name = d.pop("name")

        obj = cls(
            label_schema_uid=label_schema_uid,
            label_type=label_type,
            labels_annotators=labels_annotators,
            name=name,
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
