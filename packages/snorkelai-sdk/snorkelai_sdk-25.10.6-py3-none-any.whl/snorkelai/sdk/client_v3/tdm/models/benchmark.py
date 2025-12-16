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

from ..models.workflow_state import WorkflowState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.benchmark_metadata import BenchmarkMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Benchmark")


@attrs.define
class Benchmark:
    """
    Attributes:
        benchmark_uid (int):
        golden_response_label_schema_uid (int):
        name (str):
        workflow_uid (int):
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        metadata (Union[Unset, BenchmarkMetadata]):
        updated_at (Union[Unset, datetime.datetime]):
        workflow_state (Union[Unset, WorkflowState]):
    """

    benchmark_uid: int
    golden_response_label_schema_uid: int
    name: str
    workflow_uid: int
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "BenchmarkMetadata"] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    workflow_state: Union[Unset, WorkflowState] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.benchmark_metadata import BenchmarkMetadata  # noqa: F401
        # fmt: on
        benchmark_uid = self.benchmark_uid
        golden_response_label_schema_uid = self.golden_response_label_schema_uid
        name = self.name
        workflow_uid = self.workflow_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()
        workflow_state: Union[Unset, str] = UNSET
        if not isinstance(self.workflow_state, Unset):
            workflow_state = self.workflow_state.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_uid": benchmark_uid,
                "golden_response_label_schema_uid": golden_response_label_schema_uid,
                "name": name,
                "workflow_uid": workflow_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if workflow_state is not UNSET:
            field_dict["workflow_state"] = workflow_state

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.benchmark_metadata import BenchmarkMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark_uid = d.pop("benchmark_uid")

        golden_response_label_schema_uid = d.pop("golden_response_label_schema_uid")

        name = d.pop("name")

        workflow_uid = d.pop("workflow_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, BenchmarkMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = BenchmarkMetadata.from_dict(_metadata)

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _workflow_state = d.pop("workflow_state", UNSET)
        _workflow_state = UNSET if _workflow_state is None else _workflow_state
        workflow_state: Union[Unset, WorkflowState]
        if isinstance(_workflow_state, Unset):
            workflow_state = UNSET
        else:
            workflow_state = WorkflowState(_workflow_state)

        obj = cls(
            benchmark_uid=benchmark_uid,
            golden_response_label_schema_uid=golden_response_label_schema_uid,
            name=name,
            workflow_uid=workflow_uid,
            created_at=created_at,
            description=description,
            metadata=metadata,
            updated_at=updated_at,
            workflow_state=workflow_state,
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
