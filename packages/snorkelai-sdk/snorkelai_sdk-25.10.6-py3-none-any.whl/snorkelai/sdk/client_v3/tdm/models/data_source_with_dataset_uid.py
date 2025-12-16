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
    from ..models.data_source_with_dataset_uid_provenance import (
        DataSourceWithDatasetUidProvenance,  # noqa: F401
    )
    from ..models.datasource_metadata_base import DatasourceMetadataBase  # noqa: F401
    from ..models.load_config import LoadConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DataSourceWithDatasetUid")


@attrs.define
class DataSourceWithDatasetUid:
    """
    Attributes:
        config (LoadConfig):
        datasource_uid (int):
        ds (datetime.date):
        metadata (DatasourceMetadataBase):
        split (str):
        type (int):
        dataset_uid (Union[Unset, int]):
        datasource_name (Union[Unset, str]):
        provenance (Union[Unset, DataSourceWithDatasetUidProvenance]):
        source_uid (Union[Unset, int]):
    """

    config: "LoadConfig"
    datasource_uid: int
    ds: datetime.date
    metadata: "DatasourceMetadataBase"
    split: str
    type: int
    dataset_uid: Union[Unset, int] = UNSET
    datasource_name: Union[Unset, str] = UNSET
    provenance: Union[Unset, "DataSourceWithDatasetUidProvenance"] = UNSET
    source_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_source_with_dataset_uid_provenance import (
            DataSourceWithDatasetUidProvenance,  # noqa: F401
        )
        from ..models.datasource_metadata_base import (
            DatasourceMetadataBase,  # noqa: F401
        )
        from ..models.load_config import LoadConfig  # noqa: F401
        # fmt: on
        config = self.config.to_dict()
        datasource_uid = self.datasource_uid
        ds = self.ds.isoformat()
        metadata = self.metadata.to_dict()
        split = self.split
        type = self.type
        dataset_uid = self.dataset_uid
        datasource_name = self.datasource_name
        provenance: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.provenance, Unset):
            provenance = self.provenance.to_dict()
        source_uid = self.source_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "datasource_uid": datasource_uid,
                "ds": ds,
                "metadata": metadata,
                "split": split,
                "type": type,
            }
        )
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if datasource_name is not UNSET:
            field_dict["datasource_name"] = datasource_name
        if provenance is not UNSET:
            field_dict["provenance"] = provenance
        if source_uid is not UNSET:
            field_dict["source_uid"] = source_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_source_with_dataset_uid_provenance import (
            DataSourceWithDatasetUidProvenance,  # noqa: F401
        )
        from ..models.datasource_metadata_base import (
            DatasourceMetadataBase,  # noqa: F401
        )
        from ..models.load_config import LoadConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        config = LoadConfig.from_dict(d.pop("config"))

        datasource_uid = d.pop("datasource_uid")

        ds = isoparse(d.pop("ds")).date()

        metadata = DatasourceMetadataBase.from_dict(d.pop("metadata"))

        split = d.pop("split")

        type = d.pop("type")

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _datasource_name = d.pop("datasource_name", UNSET)
        datasource_name = UNSET if _datasource_name is None else _datasource_name

        _provenance = d.pop("provenance", UNSET)
        _provenance = UNSET if _provenance is None else _provenance
        provenance: Union[Unset, DataSourceWithDatasetUidProvenance]
        if isinstance(_provenance, Unset):
            provenance = UNSET
        else:
            provenance = DataSourceWithDatasetUidProvenance.from_dict(_provenance)

        _source_uid = d.pop("source_uid", UNSET)
        source_uid = UNSET if _source_uid is None else _source_uid

        obj = cls(
            config=config,
            datasource_uid=datasource_uid,
            ds=ds,
            metadata=metadata,
            split=split,
            type=type,
            dataset_uid=dataset_uid,
            datasource_name=datasource_name,
            provenance=provenance,
            source_uid=source_uid,
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
