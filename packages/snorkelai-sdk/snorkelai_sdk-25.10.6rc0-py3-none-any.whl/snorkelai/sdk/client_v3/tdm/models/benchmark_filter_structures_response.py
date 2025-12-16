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
    from ..models.comment_filter_structure_model import (
        CommentFilterStructureModel,  # noqa: F401
    )
    from ..models.criteria_filter_structure_model import (
        CriteriaFilterStructureModel,  # noqa: F401
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


T = TypeVar("T", bound="BenchmarkFilterStructuresResponse")


@attrs.define
class BenchmarkFilterStructuresResponse:
    """A response model for all filter structures that should be rendered
    in the Benchmarks page.
    Please make sure there's a one-to-one mapping between the fields declared here
    and BenchmarkFilterTypes.

        Attributes:
            comment (CommentFilterStructureModel): A wrapper around data returned to the FE to render comment Filter
                options.
            criteria (CriteriaFilterStructureModel): A wrapper around data returned to the FE to render criteria Filter
                options.
            field (FieldFilterStructureModel): A wrapper around data returned to the FE to render a Field Filter options.
            ground_truth (GroundTruthFilterStructureModel): A wrapper around data returned to the FE to render a Ground
                Truth Filter options.
            slice_ (SliceFilterStructureModel): A wrapper around data returned to the FE to render slice Filter options.
    """

    comment: "CommentFilterStructureModel"
    criteria: "CriteriaFilterStructureModel"
    field: "FieldFilterStructureModel"
    ground_truth: "GroundTruthFilterStructureModel"
    slice_: "SliceFilterStructureModel"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.comment_filter_structure_model import (
            CommentFilterStructureModel,  # noqa: F401
        )
        from ..models.criteria_filter_structure_model import (
            CriteriaFilterStructureModel,  # noqa: F401
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
        comment = self.comment.to_dict()
        criteria = self.criteria.to_dict()
        field = self.field.to_dict()
        ground_truth = self.ground_truth.to_dict()
        slice_ = self.slice_.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "comment": comment,
                "criteria": criteria,
                "field": field,
                "ground_truth": ground_truth,
                "slice": slice_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.comment_filter_structure_model import (
            CommentFilterStructureModel,  # noqa: F401
        )
        from ..models.criteria_filter_structure_model import (
            CriteriaFilterStructureModel,  # noqa: F401
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
        comment = CommentFilterStructureModel.from_dict(d.pop("comment"))

        criteria = CriteriaFilterStructureModel.from_dict(d.pop("criteria"))

        field = FieldFilterStructureModel.from_dict(d.pop("field"))

        ground_truth = GroundTruthFilterStructureModel.from_dict(d.pop("ground_truth"))

        slice_ = SliceFilterStructureModel.from_dict(d.pop("slice"))

        obj = cls(
            comment=comment,
            criteria=criteria,
            field=field,
            ground_truth=ground_truth,
            slice_=slice_,
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
