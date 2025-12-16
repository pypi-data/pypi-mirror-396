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


T = TypeVar("T", bound="PromptDevFilterStructuresResponse")


@attrs.define
class PromptDevFilterStructuresResponse:
    """
    Attributes:
        field (FieldFilterStructureModel): A wrapper around data returned to the FE to render a Field Filter options.
        ground_truth (GroundTruthFilterStructureModel): A wrapper around data returned to the FE to render a Ground
            Truth Filter options.
        slice_ (SliceFilterStructureModel): A wrapper around data returned to the FE to render slice Filter options.
        criteria (Union[Unset, CriteriaFilterStructureModel]): A wrapper around data returned to the FE to render
            criteria Filter options.
    """

    field: "FieldFilterStructureModel"
    ground_truth: "GroundTruthFilterStructureModel"
    slice_: "SliceFilterStructureModel"
    criteria: Union[Unset, "CriteriaFilterStructureModel"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
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
        field = self.field.to_dict()
        ground_truth = self.ground_truth.to_dict()
        slice_ = self.slice_.to_dict()
        criteria: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.criteria, Unset):
            criteria = self.criteria.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "ground_truth": ground_truth,
                "slice": slice_,
            }
        )
        if criteria is not UNSET:
            field_dict["criteria"] = criteria

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
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
        field = FieldFilterStructureModel.from_dict(d.pop("field"))

        ground_truth = GroundTruthFilterStructureModel.from_dict(d.pop("ground_truth"))

        slice_ = SliceFilterStructureModel.from_dict(d.pop("slice"))

        _criteria = d.pop("criteria", UNSET)
        _criteria = UNSET if _criteria is None else _criteria
        criteria: Union[Unset, CriteriaFilterStructureModel]
        if isinstance(_criteria, Unset):
            criteria = UNSET
        else:
            criteria = CriteriaFilterStructureModel.from_dict(_criteria)

        obj = cls(
            field=field,
            ground_truth=ground_truth,
            slice_=slice_,
            criteria=criteria,
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
