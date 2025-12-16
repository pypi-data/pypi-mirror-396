import datetime
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
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.fetched_dataset_annotation_metadata import (
        FetchedDatasetAnnotationMetadata,  # noqa: F401
    )
    from ..models.label_schema import LabelSchema  # noqa: F401
    from ..models.svc_source import SvcSource  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FetchedDatasetAnnotation")


@attrs.define
class FetchedDatasetAnnotation:
    """
    Attributes:
        annotation_uid (int):
        dataset_uid (int):
        label_schema (LabelSchema):
        source (SvcSource):
        ts (datetime.datetime):
        x_uid (str):
        annotation_task_uid (Union[Unset, int]):
        batch_uid (Union[Unset, int]):
        freeform_text (Union[Unset, str]):
        label (Union[Unset, Any]):
        metadata (Union[Unset, FetchedDatasetAnnotationMetadata]):
        split (Union[Unset, str]):
        timezone (Union[Unset, str]):
    """

    annotation_uid: int
    dataset_uid: int
    label_schema: "LabelSchema"
    source: "SvcSource"
    ts: datetime.datetime
    x_uid: str
    annotation_task_uid: Union[Unset, int] = UNSET
    batch_uid: Union[Unset, int] = UNSET
    freeform_text: Union[Unset, str] = UNSET
    label: Union[Unset, Any] = UNSET
    metadata: Union[Unset, "FetchedDatasetAnnotationMetadata"] = UNSET
    split: Union[Unset, str] = UNSET
    timezone: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.fetched_dataset_annotation_metadata import (
            FetchedDatasetAnnotationMetadata,  # noqa: F401
        )
        from ..models.label_schema import LabelSchema  # noqa: F401
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        annotation_uid = self.annotation_uid
        dataset_uid = self.dataset_uid
        label_schema = self.label_schema.to_dict()
        source = self.source.to_dict()
        ts = self.ts.isoformat()
        x_uid = self.x_uid
        annotation_task_uid = self.annotation_task_uid
        batch_uid = self.batch_uid
        freeform_text = self.freeform_text
        label = self.label
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        split = self.split
        timezone = self.timezone

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
                "dataset_uid": dataset_uid,
                "label_schema": label_schema,
                "source": source,
                "ts": ts,
                "x_uid": x_uid,
            }
        )
        if annotation_task_uid is not UNSET:
            field_dict["annotation_task_uid"] = annotation_task_uid
        if batch_uid is not UNSET:
            field_dict["batch_uid"] = batch_uid
        if freeform_text is not UNSET:
            field_dict["freeform_text"] = freeform_text
        if label is not UNSET:
            field_dict["label"] = label
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if split is not UNSET:
            field_dict["split"] = split
        if timezone is not UNSET:
            field_dict["timezone"] = timezone

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.fetched_dataset_annotation_metadata import (
            FetchedDatasetAnnotationMetadata,  # noqa: F401
        )
        from ..models.label_schema import LabelSchema  # noqa: F401
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        dataset_uid = d.pop("dataset_uid")

        label_schema = LabelSchema.from_dict(d.pop("label_schema"))

        source = SvcSource.from_dict(d.pop("source"))

        ts = isoparse(d.pop("ts"))

        x_uid = d.pop("x_uid")

        _annotation_task_uid = d.pop("annotation_task_uid", UNSET)
        annotation_task_uid = (
            UNSET if _annotation_task_uid is None else _annotation_task_uid
        )

        _batch_uid = d.pop("batch_uid", UNSET)
        batch_uid = UNSET if _batch_uid is None else _batch_uid

        _freeform_text = d.pop("freeform_text", UNSET)
        freeform_text = UNSET if _freeform_text is None else _freeform_text

        _label = d.pop("label", UNSET)
        label = UNSET if _label is None else _label

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, FetchedDatasetAnnotationMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = FetchedDatasetAnnotationMetadata.from_dict(_metadata)

        _split = d.pop("split", UNSET)
        split = UNSET if _split is None else _split

        _timezone = d.pop("timezone", UNSET)
        timezone = UNSET if _timezone is None else _timezone

        obj = cls(
            annotation_uid=annotation_uid,
            dataset_uid=dataset_uid,
            label_schema=label_schema,
            source=source,
            ts=ts,
            x_uid=x_uid,
            annotation_task_uid=annotation_task_uid,
            batch_uid=batch_uid,
            freeform_text=freeform_text,
            label=label,
            metadata=metadata,
            split=split,
            timezone=timezone,
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
