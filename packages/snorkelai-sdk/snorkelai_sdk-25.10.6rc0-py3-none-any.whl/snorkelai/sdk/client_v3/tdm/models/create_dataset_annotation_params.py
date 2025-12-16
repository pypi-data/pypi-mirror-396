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
    from ..models.create_dataset_annotation_params_metadata import (
        CreateDatasetAnnotationParamsMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateDatasetAnnotationParams")


@attrs.define
class CreateDatasetAnnotationParams:
    """
    Attributes:
        dataset_uid (int):
        label_schema_uid (int):
        x_uid (str):
        annotation_task_uid (Union[Unset, int]):
        batch_uid (Union[Unset, int]):
        convert_to_raw_format (Union[Unset, bool]):  Default: False.
        freeform_text (Union[Unset, str]):
        label (Union[Unset, Any]):
        metadata (Union[Unset, CreateDatasetAnnotationParamsMetadata]):
        source_uid (Union[Unset, int]):
        timezone (Union[Unset, str]):
        ts (Union[Unset, datetime.datetime]):
    """

    dataset_uid: int
    label_schema_uid: int
    x_uid: str
    annotation_task_uid: Union[Unset, int] = UNSET
    batch_uid: Union[Unset, int] = UNSET
    convert_to_raw_format: Union[Unset, bool] = False
    freeform_text: Union[Unset, str] = UNSET
    label: Union[Unset, Any] = UNSET
    metadata: Union[Unset, "CreateDatasetAnnotationParamsMetadata"] = UNSET
    source_uid: Union[Unset, int] = UNSET
    timezone: Union[Unset, str] = UNSET
    ts: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_dataset_annotation_params_metadata import (
            CreateDatasetAnnotationParamsMetadata,  # noqa: F401
        )
        # fmt: on
        dataset_uid = self.dataset_uid
        label_schema_uid = self.label_schema_uid
        x_uid = self.x_uid
        annotation_task_uid = self.annotation_task_uid
        batch_uid = self.batch_uid
        convert_to_raw_format = self.convert_to_raw_format
        freeform_text = self.freeform_text
        label = self.label
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        source_uid = self.source_uid
        timezone = self.timezone
        ts: Union[Unset, str] = UNSET
        if not isinstance(self.ts, Unset):
            ts = self.ts.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "label_schema_uid": label_schema_uid,
                "x_uid": x_uid,
            }
        )
        if annotation_task_uid is not UNSET:
            field_dict["annotation_task_uid"] = annotation_task_uid
        if batch_uid is not UNSET:
            field_dict["batch_uid"] = batch_uid
        if convert_to_raw_format is not UNSET:
            field_dict["convert_to_raw_format"] = convert_to_raw_format
        if freeform_text is not UNSET:
            field_dict["freeform_text"] = freeform_text
        if label is not UNSET:
            field_dict["label"] = label
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if source_uid is not UNSET:
            field_dict["source_uid"] = source_uid
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if ts is not UNSET:
            field_dict["ts"] = ts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_dataset_annotation_params_metadata import (
            CreateDatasetAnnotationParamsMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        label_schema_uid = d.pop("label_schema_uid")

        x_uid = d.pop("x_uid")

        _annotation_task_uid = d.pop("annotation_task_uid", UNSET)
        annotation_task_uid = (
            UNSET if _annotation_task_uid is None else _annotation_task_uid
        )

        _batch_uid = d.pop("batch_uid", UNSET)
        batch_uid = UNSET if _batch_uid is None else _batch_uid

        _convert_to_raw_format = d.pop("convert_to_raw_format", UNSET)
        convert_to_raw_format = (
            UNSET if _convert_to_raw_format is None else _convert_to_raw_format
        )

        _freeform_text = d.pop("freeform_text", UNSET)
        freeform_text = UNSET if _freeform_text is None else _freeform_text

        _label = d.pop("label", UNSET)
        label = UNSET if _label is None else _label

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, CreateDatasetAnnotationParamsMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateDatasetAnnotationParamsMetadata.from_dict(_metadata)

        _source_uid = d.pop("source_uid", UNSET)
        source_uid = UNSET if _source_uid is None else _source_uid

        _timezone = d.pop("timezone", UNSET)
        timezone = UNSET if _timezone is None else _timezone

        _ts = d.pop("ts", UNSET)
        _ts = UNSET if _ts is None else _ts
        ts: Union[Unset, datetime.datetime]
        if isinstance(_ts, Unset):
            ts = UNSET
        else:
            ts = isoparse(_ts)

        obj = cls(
            dataset_uid=dataset_uid,
            label_schema_uid=label_schema_uid,
            x_uid=x_uid,
            annotation_task_uid=annotation_task_uid,
            batch_uid=batch_uid,
            convert_to_raw_format=convert_to_raw_format,
            freeform_text=freeform_text,
            label=label,
            metadata=metadata,
            source_uid=source_uid,
            timezone=timezone,
            ts=ts,
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
