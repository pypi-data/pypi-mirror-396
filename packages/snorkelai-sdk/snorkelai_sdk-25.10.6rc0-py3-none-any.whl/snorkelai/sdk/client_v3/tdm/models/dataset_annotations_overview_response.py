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
    from ..models.annotator_name_id import AnnotatorNameID  # noqa: F401
    from ..models.annotator_overview_stats import AnnotatorOverviewStats  # noqa: F401
    from ..models.completion_status import CompletionStatus  # noqa: F401
    from ..models.label_stats import LabelStats  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DatasetAnnotationsOverviewResponse")


@attrs.define
class DatasetAnnotationsOverviewResponse:
    """
    Attributes:
        annotators_stats (List['AnnotatorOverviewStats']):
        completion_status (CompletionStatus):
        dataset_uid (int):
        label_distribution (List['LabelStats']):
        label_schema_uid (int):
        viewable_annotators (List['AnnotatorNameID']):
    """

    annotators_stats: List["AnnotatorOverviewStats"]
    completion_status: "CompletionStatus"
    dataset_uid: int
    label_distribution: List["LabelStats"]
    label_schema_uid: int
    viewable_annotators: List["AnnotatorNameID"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotator_name_id import AnnotatorNameID  # noqa: F401
        from ..models.annotator_overview_stats import (
            AnnotatorOverviewStats,  # noqa: F401
        )
        from ..models.completion_status import CompletionStatus  # noqa: F401
        from ..models.label_stats import LabelStats  # noqa: F401
        # fmt: on
        annotators_stats = []
        for annotators_stats_item_data in self.annotators_stats:
            annotators_stats_item = annotators_stats_item_data.to_dict()
            annotators_stats.append(annotators_stats_item)

        completion_status = self.completion_status.to_dict()
        dataset_uid = self.dataset_uid
        label_distribution = []
        for label_distribution_item_data in self.label_distribution:
            label_distribution_item = label_distribution_item_data.to_dict()
            label_distribution.append(label_distribution_item)

        label_schema_uid = self.label_schema_uid
        viewable_annotators = []
        for viewable_annotators_item_data in self.viewable_annotators:
            viewable_annotators_item = viewable_annotators_item_data.to_dict()
            viewable_annotators.append(viewable_annotators_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotators_stats": annotators_stats,
                "completion_status": completion_status,
                "dataset_uid": dataset_uid,
                "label_distribution": label_distribution,
                "label_schema_uid": label_schema_uid,
                "viewable_annotators": viewable_annotators,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotator_name_id import AnnotatorNameID  # noqa: F401
        from ..models.annotator_overview_stats import (
            AnnotatorOverviewStats,  # noqa: F401
        )
        from ..models.completion_status import CompletionStatus  # noqa: F401
        from ..models.label_stats import LabelStats  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotators_stats = []
        _annotators_stats = d.pop("annotators_stats")
        for annotators_stats_item_data in _annotators_stats:
            annotators_stats_item = AnnotatorOverviewStats.from_dict(
                annotators_stats_item_data
            )

            annotators_stats.append(annotators_stats_item)

        completion_status = CompletionStatus.from_dict(d.pop("completion_status"))

        dataset_uid = d.pop("dataset_uid")

        label_distribution = []
        _label_distribution = d.pop("label_distribution")
        for label_distribution_item_data in _label_distribution:
            label_distribution_item = LabelStats.from_dict(label_distribution_item_data)

            label_distribution.append(label_distribution_item)

        label_schema_uid = d.pop("label_schema_uid")

        viewable_annotators = []
        _viewable_annotators = d.pop("viewable_annotators")
        for viewable_annotators_item_data in _viewable_annotators:
            viewable_annotators_item = AnnotatorNameID.from_dict(
                viewable_annotators_item_data
            )

            viewable_annotators.append(viewable_annotators_item)

        obj = cls(
            annotators_stats=annotators_stats,
            completion_status=completion_status,
            dataset_uid=dataset_uid,
            label_distribution=label_distribution,
            label_schema_uid=label_schema_uid,
            viewable_annotators=viewable_annotators,
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
