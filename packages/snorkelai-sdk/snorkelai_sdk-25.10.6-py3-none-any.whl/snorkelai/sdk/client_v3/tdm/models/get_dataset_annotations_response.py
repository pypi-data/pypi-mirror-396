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
    from ..models.label_schema_annotations import LabelSchemaAnnotations  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetDatasetAnnotationsResponse")


@attrs.define
class GetDatasetAnnotationsResponse:
    """
    Attributes:
        annotations_grouped_by_label_schema (List['LabelSchemaAnnotations']):
    """

    annotations_grouped_by_label_schema: List["LabelSchemaAnnotations"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_annotations import (
            LabelSchemaAnnotations,  # noqa: F401
        )
        # fmt: on
        annotations_grouped_by_label_schema = []
        for (
            annotations_grouped_by_label_schema_item_data
        ) in self.annotations_grouped_by_label_schema:
            annotations_grouped_by_label_schema_item = (
                annotations_grouped_by_label_schema_item_data.to_dict()
            )
            annotations_grouped_by_label_schema.append(
                annotations_grouped_by_label_schema_item
            )

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotations_grouped_by_label_schema": annotations_grouped_by_label_schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_annotations import (
            LabelSchemaAnnotations,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotations_grouped_by_label_schema = []
        _annotations_grouped_by_label_schema = d.pop(
            "annotations_grouped_by_label_schema"
        )
        for (
            annotations_grouped_by_label_schema_item_data
        ) in _annotations_grouped_by_label_schema:
            annotations_grouped_by_label_schema_item = LabelSchemaAnnotations.from_dict(
                annotations_grouped_by_label_schema_item_data
            )

            annotations_grouped_by_label_schema.append(
                annotations_grouped_by_label_schema_item
            )

        obj = cls(
            annotations_grouped_by_label_schema=annotations_grouped_by_label_schema,
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
