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
    from ..models.annotator_filter_structure_model import (
        AnnotatorFilterStructureModel,  # noqa: F401
    )
    from ..models.field_filter_structure_model import (
        FieldFilterStructureModel,  # noqa: F401
    )
    from ..models.status_filter_structure_model import (
        StatusFilterStructureModel,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AnnotationTaskFilterStructuresResponse")


@attrs.define
class AnnotationTaskFilterStructuresResponse:
    """A response model for all filter structures that should be rendered
    for annotation task filter component.

        Attributes:
            annotation_task_annotator (AnnotatorFilterStructureModel): A wrapper around data returned to the FE to render
                annotator Filter options.
            annotation_task_data_point_status (StatusFilterStructureModel): A wrapper around data returned to the FE to
                render a Status Filter options.
            field (FieldFilterStructureModel): A wrapper around data returned to the FE to render a Field Filter options.
    """

    annotation_task_annotator: "AnnotatorFilterStructureModel"
    annotation_task_data_point_status: "StatusFilterStructureModel"
    field: "FieldFilterStructureModel"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotator_filter_structure_model import (
            AnnotatorFilterStructureModel,  # noqa: F401
        )
        from ..models.field_filter_structure_model import (
            FieldFilterStructureModel,  # noqa: F401
        )
        from ..models.status_filter_structure_model import (
            StatusFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        annotation_task_annotator = self.annotation_task_annotator.to_dict()
        annotation_task_data_point_status = (
            self.annotation_task_data_point_status.to_dict()
        )
        field = self.field.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_task_annotator": annotation_task_annotator,
                "annotation_task_data_point_status": annotation_task_data_point_status,
                "field": field,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotator_filter_structure_model import (
            AnnotatorFilterStructureModel,  # noqa: F401
        )
        from ..models.field_filter_structure_model import (
            FieldFilterStructureModel,  # noqa: F401
        )
        from ..models.status_filter_structure_model import (
            StatusFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotation_task_annotator = AnnotatorFilterStructureModel.from_dict(
            d.pop("annotation_task_annotator")
        )

        annotation_task_data_point_status = StatusFilterStructureModel.from_dict(
            d.pop("annotation_task_data_point_status")
        )

        field = FieldFilterStructureModel.from_dict(d.pop("field"))

        obj = cls(
            annotation_task_annotator=annotation_task_annotator,
            annotation_task_data_point_status=annotation_task_data_point_status,
            field=field,
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
