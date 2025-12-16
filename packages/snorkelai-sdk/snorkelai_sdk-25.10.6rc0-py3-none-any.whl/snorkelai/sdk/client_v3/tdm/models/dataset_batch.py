import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.dataset_batch_label_schemas import (
        DatasetBatchLabelSchemas,  # noqa: F401
    )
    from ..models.individual_annotator_statistics import (
        IndividualAnnotatorStatistics,  # noqa: F401
    )
    from ..models.metadata import Metadata  # noqa: F401
    from ..models.svc_source import SvcSource  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DatasetBatch")


@attrs.define
class DatasetBatch:
    """
    Attributes:
        batch_size (int):
        batch_uid (int):
        dataset_uid (int):
        split (str):
        ts (datetime.datetime):
        annotator_progress (Union[Unset, List['IndividualAnnotatorStatistics']]):
        assignees (Union[Unset, List[str]]):
        dataset_name (Union[Unset, str]):
        expert_source_uid (Union[Unset, int]):
        label_schemas (Union[Unset, DatasetBatchLabelSchemas]):
        metadata (Union[Unset, Metadata]):
        name (Union[Unset, str]):
        sources (Union[Unset, List['SvcSource']]):
        user_uid (Union[Unset, int]):
    """

    batch_size: int
    batch_uid: int
    dataset_uid: int
    split: str
    ts: datetime.datetime
    annotator_progress: Union[Unset, List["IndividualAnnotatorStatistics"]] = UNSET
    assignees: Union[Unset, List[str]] = UNSET
    dataset_name: Union[Unset, str] = UNSET
    expert_source_uid: Union[Unset, int] = UNSET
    label_schemas: Union[Unset, "DatasetBatchLabelSchemas"] = UNSET
    metadata: Union[Unset, "Metadata"] = UNSET
    name: Union[Unset, str] = UNSET
    sources: Union[Unset, List["SvcSource"]] = UNSET
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.dataset_batch_label_schemas import (
            DatasetBatchLabelSchemas,  # noqa: F401
        )
        from ..models.individual_annotator_statistics import (
            IndividualAnnotatorStatistics,  # noqa: F401
        )
        from ..models.metadata import Metadata  # noqa: F401
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        batch_size = self.batch_size
        batch_uid = self.batch_uid
        dataset_uid = self.dataset_uid
        split = self.split
        ts = self.ts.isoformat()
        annotator_progress: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.annotator_progress, Unset):
            annotator_progress = []
            for annotator_progress_item_data in self.annotator_progress:
                annotator_progress_item = annotator_progress_item_data.to_dict()
                annotator_progress.append(annotator_progress_item)

        assignees: Union[Unset, List[str]] = UNSET
        if not isinstance(self.assignees, Unset):
            assignees = self.assignees

        dataset_name = self.dataset_name
        expert_source_uid = self.expert_source_uid
        label_schemas: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_schemas, Unset):
            label_schemas = self.label_schemas.to_dict()
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        name = self.name
        sources: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sources, Unset):
            sources = []
            for sources_item_data in self.sources:
                sources_item = sources_item_data.to_dict()
                sources.append(sources_item)

        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "batch_size": batch_size,
                "batch_uid": batch_uid,
                "dataset_uid": dataset_uid,
                "split": split,
                "ts": ts,
            }
        )
        if annotator_progress is not UNSET:
            field_dict["annotator_progress"] = annotator_progress
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if dataset_name is not UNSET:
            field_dict["dataset_name"] = dataset_name
        if expert_source_uid is not UNSET:
            field_dict["expert_source_uid"] = expert_source_uid
        if label_schemas is not UNSET:
            field_dict["label_schemas"] = label_schemas
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if name is not UNSET:
            field_dict["name"] = name
        if sources is not UNSET:
            field_dict["sources"] = sources
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.dataset_batch_label_schemas import (
            DatasetBatchLabelSchemas,  # noqa: F401
        )
        from ..models.individual_annotator_statistics import (
            IndividualAnnotatorStatistics,  # noqa: F401
        )
        from ..models.metadata import Metadata  # noqa: F401
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        batch_size = d.pop("batch_size")

        batch_uid = d.pop("batch_uid")

        dataset_uid = d.pop("dataset_uid")

        split = d.pop("split")

        ts = isoparse(d.pop("ts"))

        _annotator_progress = d.pop("annotator_progress", UNSET)
        annotator_progress = []
        _annotator_progress = (
            UNSET if _annotator_progress is None else _annotator_progress
        )
        for annotator_progress_item_data in _annotator_progress or []:
            annotator_progress_item = IndividualAnnotatorStatistics.from_dict(
                annotator_progress_item_data
            )

            annotator_progress.append(annotator_progress_item)

        _assignees = d.pop("assignees", UNSET)
        assignees = cast(List[str], UNSET if _assignees is None else _assignees)

        _dataset_name = d.pop("dataset_name", UNSET)
        dataset_name = UNSET if _dataset_name is None else _dataset_name

        _expert_source_uid = d.pop("expert_source_uid", UNSET)
        expert_source_uid = UNSET if _expert_source_uid is None else _expert_source_uid

        _label_schemas = d.pop("label_schemas", UNSET)
        _label_schemas = UNSET if _label_schemas is None else _label_schemas
        label_schemas: Union[Unset, DatasetBatchLabelSchemas]
        if isinstance(_label_schemas, Unset):
            label_schemas = UNSET
        else:
            label_schemas = DatasetBatchLabelSchemas.from_dict(_label_schemas)

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        _name = d.pop("name", UNSET)
        name = UNSET if _name is None else _name

        _sources = d.pop("sources", UNSET)
        sources = []
        _sources = UNSET if _sources is None else _sources
        for sources_item_data in _sources or []:
            sources_item = SvcSource.from_dict(sources_item_data)

            sources.append(sources_item)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            batch_size=batch_size,
            batch_uid=batch_uid,
            dataset_uid=dataset_uid,
            split=split,
            ts=ts,
            annotator_progress=annotator_progress,
            assignees=assignees,
            dataset_name=dataset_name,
            expert_source_uid=expert_source_uid,
            label_schemas=label_schemas,
            metadata=metadata,
            name=name,
            sources=sources,
            user_uid=user_uid,
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
