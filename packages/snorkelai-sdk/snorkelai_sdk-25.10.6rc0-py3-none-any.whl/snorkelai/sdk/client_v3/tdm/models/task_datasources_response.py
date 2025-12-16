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
    from ..models.task_datasources_response_config import (
        TaskDatasourcesResponseConfig,  # noqa: F401
    )
    from ..models.task_datasources_response_metadata import (
        TaskDatasourcesResponseMetadata,  # noqa: F401
    )
    from ..models.task_datasources_response_provenance import (
        TaskDatasourcesResponseProvenance,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="TaskDatasourcesResponse")


@attrs.define
class TaskDatasourcesResponse:
    """
    Attributes:
        config (TaskDatasourcesResponseConfig):
        datasource_uid (int):
        ds (datetime.date):
        is_active (bool):
        metadata (TaskDatasourcesResponseMetadata):
        split (str):
        supports_dev (bool):
        type (int):
        n_datapoints (Union[Unset, int]):
        n_docs (Union[Unset, int]):
        n_gt_labels (Union[Unset, int]):
        provenance (Union[Unset, TaskDatasourcesResponseProvenance]):
    """

    config: "TaskDatasourcesResponseConfig"
    datasource_uid: int
    ds: datetime.date
    is_active: bool
    metadata: "TaskDatasourcesResponseMetadata"
    split: str
    supports_dev: bool
    type: int
    n_datapoints: Union[Unset, int] = UNSET
    n_docs: Union[Unset, int] = UNSET
    n_gt_labels: Union[Unset, int] = UNSET
    provenance: Union[Unset, "TaskDatasourcesResponseProvenance"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.task_datasources_response_config import (
            TaskDatasourcesResponseConfig,  # noqa: F401
        )
        from ..models.task_datasources_response_metadata import (
            TaskDatasourcesResponseMetadata,  # noqa: F401
        )
        from ..models.task_datasources_response_provenance import (
            TaskDatasourcesResponseProvenance,  # noqa: F401
        )
        # fmt: on
        config = self.config.to_dict()
        datasource_uid = self.datasource_uid
        ds = self.ds.isoformat()
        is_active = self.is_active
        metadata = self.metadata.to_dict()
        split = self.split
        supports_dev = self.supports_dev
        type = self.type
        n_datapoints = self.n_datapoints
        n_docs = self.n_docs
        n_gt_labels = self.n_gt_labels
        provenance: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.provenance, Unset):
            provenance = self.provenance.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "datasource_uid": datasource_uid,
                "ds": ds,
                "is_active": is_active,
                "metadata": metadata,
                "split": split,
                "supports_dev": supports_dev,
                "type": type,
            }
        )
        if n_datapoints is not UNSET:
            field_dict["n_datapoints"] = n_datapoints
        if n_docs is not UNSET:
            field_dict["n_docs"] = n_docs
        if n_gt_labels is not UNSET:
            field_dict["n_gt_labels"] = n_gt_labels
        if provenance is not UNSET:
            field_dict["provenance"] = provenance

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.task_datasources_response_config import (
            TaskDatasourcesResponseConfig,  # noqa: F401
        )
        from ..models.task_datasources_response_metadata import (
            TaskDatasourcesResponseMetadata,  # noqa: F401
        )
        from ..models.task_datasources_response_provenance import (
            TaskDatasourcesResponseProvenance,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        config = TaskDatasourcesResponseConfig.from_dict(d.pop("config"))

        datasource_uid = d.pop("datasource_uid")

        ds = isoparse(d.pop("ds")).date()

        is_active = d.pop("is_active")

        metadata = TaskDatasourcesResponseMetadata.from_dict(d.pop("metadata"))

        split = d.pop("split")

        supports_dev = d.pop("supports_dev")

        type = d.pop("type")

        _n_datapoints = d.pop("n_datapoints", UNSET)
        n_datapoints = UNSET if _n_datapoints is None else _n_datapoints

        _n_docs = d.pop("n_docs", UNSET)
        n_docs = UNSET if _n_docs is None else _n_docs

        _n_gt_labels = d.pop("n_gt_labels", UNSET)
        n_gt_labels = UNSET if _n_gt_labels is None else _n_gt_labels

        _provenance = d.pop("provenance", UNSET)
        _provenance = UNSET if _provenance is None else _provenance
        provenance: Union[Unset, TaskDatasourcesResponseProvenance]
        if isinstance(_provenance, Unset):
            provenance = UNSET
        else:
            provenance = TaskDatasourcesResponseProvenance.from_dict(_provenance)

        obj = cls(
            config=config,
            datasource_uid=datasource_uid,
            ds=ds,
            is_active=is_active,
            metadata=metadata,
            split=split,
            supports_dev=supports_dev,
            type=type,
            n_datapoints=n_datapoints,
            n_docs=n_docs,
            n_gt_labels=n_gt_labels,
            provenance=provenance,
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
