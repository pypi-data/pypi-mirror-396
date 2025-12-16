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
    from ..models.label_schema_annotator_summary import (
        LabelSchemaAnnotatorSummary,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GetAnnotationsByXUidResponse")


@attrs.define
class GetAnnotationsByXUidResponse:
    """
    Attributes:
        aggregated_annotators_per_label_schema (List['LabelSchemaAnnotatorSummary']):
        x_uid (str):
    """

    aggregated_annotators_per_label_schema: List["LabelSchemaAnnotatorSummary"]
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_annotator_summary import (
            LabelSchemaAnnotatorSummary,  # noqa: F401
        )
        # fmt: on
        aggregated_annotators_per_label_schema = []
        for (
            aggregated_annotators_per_label_schema_item_data
        ) in self.aggregated_annotators_per_label_schema:
            aggregated_annotators_per_label_schema_item = (
                aggregated_annotators_per_label_schema_item_data.to_dict()
            )
            aggregated_annotators_per_label_schema.append(
                aggregated_annotators_per_label_schema_item
            )

        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aggregated_annotators_per_label_schema": aggregated_annotators_per_label_schema,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_annotator_summary import (
            LabelSchemaAnnotatorSummary,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        aggregated_annotators_per_label_schema = []
        _aggregated_annotators_per_label_schema = d.pop(
            "aggregated_annotators_per_label_schema"
        )
        for (
            aggregated_annotators_per_label_schema_item_data
        ) in _aggregated_annotators_per_label_schema:
            aggregated_annotators_per_label_schema_item = (
                LabelSchemaAnnotatorSummary.from_dict(
                    aggregated_annotators_per_label_schema_item_data
                )
            )

            aggregated_annotators_per_label_schema.append(
                aggregated_annotators_per_label_schema_item
            )

        x_uid = d.pop("x_uid")

        obj = cls(
            aggregated_annotators_per_label_schema=aggregated_annotators_per_label_schema,
            x_uid=x_uid,
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
