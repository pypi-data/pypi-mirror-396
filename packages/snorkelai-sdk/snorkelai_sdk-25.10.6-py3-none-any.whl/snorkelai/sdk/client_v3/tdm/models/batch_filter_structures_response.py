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
    from ..models.annotator_agreement_filter_structure_model import (
        AnnotatorAgreementFilterStructureModel,  # noqa: F401
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


T = TypeVar("T", bound="BatchFilterStructuresResponse")


@attrs.define
class BatchFilterStructuresResponse:
    """A response model for all filter structures that should be rendered
    in the Dataset Batch Annotation page.
    Please make sure there's a one-to-one mapping between the fields declared here
    and BatchFilterTypes.

        Attributes:
            field (FieldFilterStructureModel): A wrapper around data returned to the FE to render a Field Filter options.
            slice_ (SliceFilterStructureModel): A wrapper around data returned to the FE to render slice Filter options.
            annotation (Union[Unset, AnnotationFilterStructureModel]): A wrapper around data returned to the FE to render a
                Annotation Filter options.
            annotator_agreement (Union[Unset, AnnotatorAgreementFilterStructureModel]): A wrapper around data returned to
                the FE to render a Annotator Agreement Filter options.
            comment (Union[Unset, CommentFilterStructureModel]): A wrapper around data returned to the FE to render comment
                Filter options.
            ground_truth (Union[Unset, GroundTruthFilterStructureModel]): A wrapper around data returned to the FE to render
                a Ground Truth Filter options.
    """

    field: "FieldFilterStructureModel"
    slice_: "SliceFilterStructureModel"
    annotation: Union[Unset, "AnnotationFilterStructureModel"] = UNSET
    annotator_agreement: Union[Unset, "AnnotatorAgreementFilterStructureModel"] = UNSET
    comment: Union[Unset, "CommentFilterStructureModel"] = UNSET
    ground_truth: Union[Unset, "GroundTruthFilterStructureModel"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_filter_structure_model import (
            AnnotationFilterStructureModel,  # noqa: F401
        )
        from ..models.annotator_agreement_filter_structure_model import (
            AnnotatorAgreementFilterStructureModel,  # noqa: F401
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
        field = self.field.to_dict()
        slice_ = self.slice_.to_dict()
        annotation: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation, Unset):
            annotation = self.annotation.to_dict()
        annotator_agreement: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotator_agreement, Unset):
            annotator_agreement = self.annotator_agreement.to_dict()
        comment: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.comment, Unset):
            comment = self.comment.to_dict()
        ground_truth: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ground_truth, Unset):
            ground_truth = self.ground_truth.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "slice": slice_,
            }
        )
        if annotation is not UNSET:
            field_dict["annotation"] = annotation
        if annotator_agreement is not UNSET:
            field_dict["annotator_agreement"] = annotator_agreement
        if comment is not UNSET:
            field_dict["comment"] = comment
        if ground_truth is not UNSET:
            field_dict["ground_truth"] = ground_truth

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_filter_structure_model import (
            AnnotationFilterStructureModel,  # noqa: F401
        )
        from ..models.annotator_agreement_filter_structure_model import (
            AnnotatorAgreementFilterStructureModel,  # noqa: F401
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
        field = FieldFilterStructureModel.from_dict(d.pop("field"))

        slice_ = SliceFilterStructureModel.from_dict(d.pop("slice"))

        _annotation = d.pop("annotation", UNSET)
        _annotation = UNSET if _annotation is None else _annotation
        annotation: Union[Unset, AnnotationFilterStructureModel]
        if isinstance(_annotation, Unset):
            annotation = UNSET
        else:
            annotation = AnnotationFilterStructureModel.from_dict(_annotation)

        _annotator_agreement = d.pop("annotator_agreement", UNSET)
        _annotator_agreement = (
            UNSET if _annotator_agreement is None else _annotator_agreement
        )
        annotator_agreement: Union[Unset, AnnotatorAgreementFilterStructureModel]
        if isinstance(_annotator_agreement, Unset):
            annotator_agreement = UNSET
        else:
            annotator_agreement = AnnotatorAgreementFilterStructureModel.from_dict(
                _annotator_agreement
            )

        _comment = d.pop("comment", UNSET)
        _comment = UNSET if _comment is None else _comment
        comment: Union[Unset, CommentFilterStructureModel]
        if isinstance(_comment, Unset):
            comment = UNSET
        else:
            comment = CommentFilterStructureModel.from_dict(_comment)

        _ground_truth = d.pop("ground_truth", UNSET)
        _ground_truth = UNSET if _ground_truth is None else _ground_truth
        ground_truth: Union[Unset, GroundTruthFilterStructureModel]
        if isinstance(_ground_truth, Unset):
            ground_truth = UNSET
        else:
            ground_truth = GroundTruthFilterStructureModel.from_dict(_ground_truth)

        obj = cls(
            field=field,
            slice_=slice_,
            annotation=annotation,
            annotator_agreement=annotator_agreement,
            comment=comment,
            ground_truth=ground_truth,
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
