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
    from ..models.dataset_batch_metadata import DatasetBatchMetadata  # noqa: F401
    from ..models.fetched_dataset_annotation import (
        FetchedDatasetAnnotation,  # noqa: F401
    )
    from ..models.svc_source import SvcSource  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LabelSchemaAnnotations")


@attrs.define
class LabelSchemaAnnotations:
    """
    Attributes:
        annotations (List['FetchedDatasetAnnotation']):
        label_schema_uid (int):
        sources (List['SvcSource']):
        batch_metadata (Union[Unset, List['DatasetBatchMetadata']]):
    """

    annotations: List["FetchedDatasetAnnotation"]
    label_schema_uid: int
    sources: List["SvcSource"]
    batch_metadata: Union[Unset, List["DatasetBatchMetadata"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.dataset_batch_metadata import DatasetBatchMetadata  # noqa: F401
        from ..models.fetched_dataset_annotation import (
            FetchedDatasetAnnotation,  # noqa: F401
        )
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        annotations = []
        for annotations_item_data in self.annotations:
            annotations_item = annotations_item_data.to_dict()
            annotations.append(annotations_item)

        label_schema_uid = self.label_schema_uid
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        batch_metadata: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.batch_metadata, Unset):
            batch_metadata = []
            for batch_metadata_item_data in self.batch_metadata:
                batch_metadata_item = batch_metadata_item_data.to_dict()
                batch_metadata.append(batch_metadata_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotations": annotations,
                "label_schema_uid": label_schema_uid,
                "sources": sources,
            }
        )
        if batch_metadata is not UNSET:
            field_dict["batch_metadata"] = batch_metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.dataset_batch_metadata import DatasetBatchMetadata  # noqa: F401
        from ..models.fetched_dataset_annotation import (
            FetchedDatasetAnnotation,  # noqa: F401
        )
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotations = []
        _annotations = d.pop("annotations")
        for annotations_item_data in _annotations:
            annotations_item = FetchedDatasetAnnotation.from_dict(annotations_item_data)

            annotations.append(annotations_item)

        label_schema_uid = d.pop("label_schema_uid")

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = SvcSource.from_dict(sources_item_data)

            sources.append(sources_item)

        _batch_metadata = d.pop("batch_metadata", UNSET)
        batch_metadata = []
        _batch_metadata = UNSET if _batch_metadata is None else _batch_metadata
        for batch_metadata_item_data in _batch_metadata or []:
            batch_metadata_item = DatasetBatchMetadata.from_dict(
                batch_metadata_item_data
            )

            batch_metadata.append(batch_metadata_item)

        obj = cls(
            annotations=annotations,
            label_schema_uid=label_schema_uid,
            sources=sources,
            batch_metadata=batch_metadata,
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
