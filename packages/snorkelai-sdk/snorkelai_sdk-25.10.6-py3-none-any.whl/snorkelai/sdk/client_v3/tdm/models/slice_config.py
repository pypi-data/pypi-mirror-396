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

from ..models.dataset_transform_type import DatasetTransformType

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_filter_schema import AnnotationFilterSchema  # noqa: F401
    from ..models.annotator_agreement_filter_schema import (
        AnnotatorAgreementFilterSchema,  # noqa: F401
    )
    from ..models.annotator_filter_schema import AnnotatorFilterSchema  # noqa: F401
    from ..models.cluster_filter_schema import ClusterFilterSchema  # noqa: F401
    from ..models.combiner_transform_config import CombinerTransformConfig  # noqa: F401
    from ..models.comment_filter_schema import CommentFilterSchema  # noqa: F401
    from ..models.criteria_filter_schema import CriteriaFilterSchema  # noqa: F401
    from ..models.data_loader_for_index_provenance import (
        DataLoaderForIndexProvenance,  # noqa: F401
    )
    from ..models.dataset_batch_sorter_config import (
        DatasetBatchSorterConfig,  # noqa: F401
    )
    from ..models.field_filter_schema import FieldFilterSchema  # noqa: F401
    from ..models.filter_graph_config import FilterGraphConfig  # noqa: F401
    from ..models.filter_string_config import FilterStringConfig  # noqa: F401
    from ..models.first_n_config import FirstNConfig  # noqa: F401
    from ..models.ground_truth_filter_schema import (
        GroundTruthFilterSchema,  # noqa: F401
    )
    from ..models.margin_distance_filter_schema import (
        MarginDistanceFilterSchema,  # noqa: F401
    )
    from ..models.model_filter_schema import ModelFilterSchema  # noqa: F401
    from ..models.slice_filter_schema import SliceFilterSchema  # noqa: F401
    from ..models.status_filter_schema import StatusFilterSchema  # noqa: F401
    from ..models.template_filter_schema import TemplateFilterSchema  # noqa: F401
    from ..models.vds_sorter_config import VDSSorterConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SliceConfig")


@attrs.define
class SliceConfig:
    """
    Attributes:
        transform_config (Union['AnnotationFilterSchema', 'AnnotatorAgreementFilterSchema', 'AnnotatorFilterSchema',
            'ClusterFilterSchema', 'CombinerTransformConfig', 'CommentFilterSchema', 'CriteriaFilterSchema',
            'DataLoaderForIndexProvenance', 'DatasetBatchSorterConfig', 'FieldFilterSchema', 'FilterGraphConfig',
            'FilterStringConfig', 'FirstNConfig', 'GroundTruthFilterSchema', 'MarginDistanceFilterSchema',
            'ModelFilterSchema', 'SliceFilterSchema', 'StatusFilterSchema', 'TemplateFilterSchema', 'VDSSorterConfig']):
        transform_type (DatasetTransformType):
    """

    transform_config: Union[
        "AnnotationFilterSchema",
        "AnnotatorAgreementFilterSchema",
        "AnnotatorFilterSchema",
        "ClusterFilterSchema",
        "CombinerTransformConfig",
        "CommentFilterSchema",
        "CriteriaFilterSchema",
        "DataLoaderForIndexProvenance",
        "DatasetBatchSorterConfig",
        "FieldFilterSchema",
        "FilterGraphConfig",
        "FilterStringConfig",
        "FirstNConfig",
        "GroundTruthFilterSchema",
        "MarginDistanceFilterSchema",
        "ModelFilterSchema",
        "SliceFilterSchema",
        "StatusFilterSchema",
        "TemplateFilterSchema",
        "VDSSorterConfig",
    ]
    transform_type: DatasetTransformType
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_filter_schema import (
            AnnotationFilterSchema,  # noqa: F401
        )
        from ..models.annotator_agreement_filter_schema import (
            AnnotatorAgreementFilterSchema,  # noqa: F401
        )
        from ..models.annotator_filter_schema import AnnotatorFilterSchema  # noqa: F401
        from ..models.cluster_filter_schema import ClusterFilterSchema  # noqa: F401
        from ..models.combiner_transform_config import (
            CombinerTransformConfig,  # noqa: F401
        )
        from ..models.comment_filter_schema import CommentFilterSchema  # noqa: F401
        from ..models.criteria_filter_schema import CriteriaFilterSchema  # noqa: F401
        from ..models.data_loader_for_index_provenance import (
            DataLoaderForIndexProvenance,  # noqa: F401
        )
        from ..models.dataset_batch_sorter_config import (
            DatasetBatchSorterConfig,  # noqa: F401
        )
        from ..models.field_filter_schema import FieldFilterSchema  # noqa: F401
        from ..models.filter_graph_config import FilterGraphConfig  # noqa: F401
        from ..models.filter_string_config import FilterStringConfig  # noqa: F401
        from ..models.first_n_config import FirstNConfig  # noqa: F401
        from ..models.ground_truth_filter_schema import (
            GroundTruthFilterSchema,  # noqa: F401
        )
        from ..models.margin_distance_filter_schema import (
            MarginDistanceFilterSchema,  # noqa: F401
        )
        from ..models.model_filter_schema import ModelFilterSchema  # noqa: F401
        from ..models.slice_filter_schema import SliceFilterSchema  # noqa: F401
        from ..models.status_filter_schema import StatusFilterSchema  # noqa: F401
        from ..models.template_filter_schema import TemplateFilterSchema  # noqa: F401
        from ..models.vds_sorter_config import VDSSorterConfig  # noqa: F401
        # fmt: on
        transform_config: Dict[str, Any]
        if isinstance(self.transform_config, FilterStringConfig):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, GroundTruthFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, CommentFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, SliceFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, FieldFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, ClusterFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, AnnotationFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, AnnotatorAgreementFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, ModelFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, MarginDistanceFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, CriteriaFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, TemplateFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, AnnotatorFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, StatusFilterSchema):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, FilterGraphConfig):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, DataLoaderForIndexProvenance):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, FirstNConfig):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, CombinerTransformConfig):
            transform_config = self.transform_config.to_dict()
        elif isinstance(self.transform_config, DatasetBatchSorterConfig):
            transform_config = self.transform_config.to_dict()
        else:
            transform_config = self.transform_config.to_dict()

        transform_type = self.transform_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "transform_config": transform_config,
                "transform_type": transform_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_filter_schema import (
            AnnotationFilterSchema,  # noqa: F401
        )
        from ..models.annotator_agreement_filter_schema import (
            AnnotatorAgreementFilterSchema,  # noqa: F401
        )
        from ..models.annotator_filter_schema import AnnotatorFilterSchema  # noqa: F401
        from ..models.cluster_filter_schema import ClusterFilterSchema  # noqa: F401
        from ..models.combiner_transform_config import (
            CombinerTransformConfig,  # noqa: F401
        )
        from ..models.comment_filter_schema import CommentFilterSchema  # noqa: F401
        from ..models.criteria_filter_schema import CriteriaFilterSchema  # noqa: F401
        from ..models.data_loader_for_index_provenance import (
            DataLoaderForIndexProvenance,  # noqa: F401
        )
        from ..models.dataset_batch_sorter_config import (
            DatasetBatchSorterConfig,  # noqa: F401
        )
        from ..models.field_filter_schema import FieldFilterSchema  # noqa: F401
        from ..models.filter_graph_config import FilterGraphConfig  # noqa: F401
        from ..models.filter_string_config import FilterStringConfig  # noqa: F401
        from ..models.first_n_config import FirstNConfig  # noqa: F401
        from ..models.ground_truth_filter_schema import (
            GroundTruthFilterSchema,  # noqa: F401
        )
        from ..models.margin_distance_filter_schema import (
            MarginDistanceFilterSchema,  # noqa: F401
        )
        from ..models.model_filter_schema import ModelFilterSchema  # noqa: F401
        from ..models.slice_filter_schema import SliceFilterSchema  # noqa: F401
        from ..models.status_filter_schema import StatusFilterSchema  # noqa: F401
        from ..models.template_filter_schema import TemplateFilterSchema  # noqa: F401
        from ..models.vds_sorter_config import VDSSorterConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()

        def _parse_transform_config(
            data: object,
        ) -> Union[
            "AnnotationFilterSchema",
            "AnnotatorAgreementFilterSchema",
            "AnnotatorFilterSchema",
            "ClusterFilterSchema",
            "CombinerTransformConfig",
            "CommentFilterSchema",
            "CriteriaFilterSchema",
            "DataLoaderForIndexProvenance",
            "DatasetBatchSorterConfig",
            "FieldFilterSchema",
            "FilterGraphConfig",
            "FilterStringConfig",
            "FirstNConfig",
            "GroundTruthFilterSchema",
            "MarginDistanceFilterSchema",
            "ModelFilterSchema",
            "SliceFilterSchema",
            "StatusFilterSchema",
            "TemplateFilterSchema",
            "VDSSorterConfig",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_0 = FilterStringConfig.from_dict(data)

                return transform_config_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_1 = GroundTruthFilterSchema.from_dict(data)

                return transform_config_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_2 = CommentFilterSchema.from_dict(data)

                return transform_config_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_3 = SliceFilterSchema.from_dict(data)

                return transform_config_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_4 = FieldFilterSchema.from_dict(data)

                return transform_config_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_5 = ClusterFilterSchema.from_dict(data)

                return transform_config_type_5
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_6 = AnnotationFilterSchema.from_dict(data)

                return transform_config_type_6
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_7 = AnnotatorAgreementFilterSchema.from_dict(data)

                return transform_config_type_7
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_8 = ModelFilterSchema.from_dict(data)

                return transform_config_type_8
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_9 = MarginDistanceFilterSchema.from_dict(data)

                return transform_config_type_9
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_10 = CriteriaFilterSchema.from_dict(data)

                return transform_config_type_10
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_11 = TemplateFilterSchema.from_dict(data)

                return transform_config_type_11
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_12 = AnnotatorFilterSchema.from_dict(data)

                return transform_config_type_12
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_13 = StatusFilterSchema.from_dict(data)

                return transform_config_type_13
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_14 = FilterGraphConfig.from_dict(data)

                return transform_config_type_14
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_15 = DataLoaderForIndexProvenance.from_dict(data)

                return transform_config_type_15
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_16 = FirstNConfig.from_dict(data)

                return transform_config_type_16
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_17 = CombinerTransformConfig.from_dict(data)

                return transform_config_type_17
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                transform_config_type_18 = DatasetBatchSorterConfig.from_dict(data)

                return transform_config_type_18
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            transform_config_type_19 = VDSSorterConfig.from_dict(data)

            return transform_config_type_19

        transform_config = _parse_transform_config(d.pop("transform_config"))

        transform_type = DatasetTransformType(d.pop("transform_type"))

        obj = cls(
            transform_config=transform_config,
            transform_type=transform_type,
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
