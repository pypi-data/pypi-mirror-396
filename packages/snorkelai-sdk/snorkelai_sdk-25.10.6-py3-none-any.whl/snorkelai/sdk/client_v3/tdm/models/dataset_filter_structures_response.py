from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_filter_structure_model import (
        AnnotationFilterStructureModel,  # noqa: F401
    )
    from ..models.comment_filter_structure_model import (
        CommentFilterStructureModel,  # noqa: F401
    )
    from ..models.field_filter_structure_model import (
        FieldFilterStructureModel,  # noqa: F401
    )
    from ..models.ground_truth_filter_structure_model import (
        GroundTruthFilterStructureModel,  # noqa: F401
    )
    from ..models.slice_filter_structure_model import (
        SliceFilterStructureModel,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DatasetFilterStructuresResponse")


@attrs.define
class DatasetFilterStructuresResponse:
    """A response model for all filter structures that should be rendered
    for a dataset filter component.

        Attributes:
            ground_truth (GroundTruthFilterStructureModel): A wrapper around data returned to the FE to render a Ground
                Truth Filter options.
            slice_ (SliceFilterStructureModel): A wrapper around data returned to the FE to render slice Filter options.
            annotation (Union[Unset, AnnotationFilterStructureModel]): A wrapper around data returned to the FE to render a
                Annotation Filter options.
            comment (Union[Unset, CommentFilterStructureModel]): A wrapper around data returned to the FE to render comment
                Filter options.
            field (Union[Unset, FieldFilterStructureModel]): A wrapper around data returned to the FE to render a Field
                Filter options.
    """

    ground_truth: "GroundTruthFilterStructureModel"
    slice_: "SliceFilterStructureModel"
    annotation: Union[Unset, "AnnotationFilterStructureModel"] = UNSET
    comment: Union[Unset, "CommentFilterStructureModel"] = UNSET
    field: Union[Unset, "FieldFilterStructureModel"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_filter_structure_model import (
            AnnotationFilterStructureModel,  # noqa: F401
        )
        from ..models.comment_filter_structure_model import (
            CommentFilterStructureModel,  # noqa: F401
        )
        from ..models.field_filter_structure_model import (
            FieldFilterStructureModel,  # noqa: F401
        )
        from ..models.ground_truth_filter_structure_model import (
            GroundTruthFilterStructureModel,  # noqa: F401
        )
        from ..models.slice_filter_structure_model import (
            SliceFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        ground_truth = self.ground_truth.to_dict()
        slice_ = self.slice_.to_dict()
        annotation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation, Unset):
            annotation = self.annotation.to_dict()
        comment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.comment, Unset):
            comment = self.comment.to_dict()
        field: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.field, Unset):
            field = self.field.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ground_truth": ground_truth,
                "slice": slice_,
            }
        )
        if annotation is not UNSET:
            field_dict["annotation"] = annotation
        if comment is not UNSET:
            field_dict["comment"] = comment
        if field is not UNSET:
            field_dict["field"] = field

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_filter_structure_model import (
            AnnotationFilterStructureModel,  # noqa: F401
        )
        from ..models.comment_filter_structure_model import (
            CommentFilterStructureModel,  # noqa: F401
        )
        from ..models.field_filter_structure_model import (
            FieldFilterStructureModel,  # noqa: F401
        )
        from ..models.ground_truth_filter_structure_model import (
            GroundTruthFilterStructureModel,  # noqa: F401
        )
        from ..models.slice_filter_structure_model import (
            SliceFilterStructureModel,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        ground_truth = GroundTruthFilterStructureModel.from_dict(d.pop("ground_truth"))

        slice_ = SliceFilterStructureModel.from_dict(d.pop("slice"))

        _annotation = d.pop("annotation", UNSET)
        _annotation = UNSET if _annotation is None else _annotation
        annotation: Union[Unset, AnnotationFilterStructureModel]
        if isinstance(_annotation, Unset):
            annotation = UNSET
        else:
            annotation = AnnotationFilterStructureModel.from_dict(_annotation)

        _comment = d.pop("comment", UNSET)
        _comment = UNSET if _comment is None else _comment
        comment: Union[Unset, CommentFilterStructureModel]
        if isinstance(_comment, Unset):
            comment = UNSET
        else:
            comment = CommentFilterStructureModel.from_dict(_comment)

        _field = d.pop("field", UNSET)
        _field = UNSET if _field is None else _field
        field: Union[Unset, FieldFilterStructureModel]
        if isinstance(_field, Unset):
            field = UNSET
        else:
            field = FieldFilterStructureModel.from_dict(_field)

        obj = cls(
            ground_truth=ground_truth,
            slice_=slice_,
            annotation=annotation,
            comment=comment,
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
