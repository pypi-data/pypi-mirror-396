from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.datasource_type import DatasourceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="RemoteStaticAssetUploadRequest")


@attrs.define
class RemoteStaticAssetUploadRequest:
    """
    Attributes:
        source (str): Path to the data source
        source_type (DatasourceType): Types of data sources that can be connected to.
        target_path (str): Location for storing the data in Snorkel's internal storage
        type (Literal['static_asset']):
        data_connector_config_uid (Union[Unset, int]):
        dataset_uid (Union[Unset, int]):
        overwrite_existing (Union[Unset, bool]):  Default: False.
    """

    source: str
    source_type: DatasourceType
    target_path: str
    type: Literal["static_asset"]
    data_connector_config_uid: Union[Unset, int] = UNSET
    dataset_uid: Union[Unset, int] = UNSET
    overwrite_existing: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source = self.source
        source_type = self.source_type.value
        target_path = self.target_path
        type = self.type
        data_connector_config_uid = self.data_connector_config_uid
        dataset_uid = self.dataset_uid
        overwrite_existing = self.overwrite_existing

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "source_type": source_type,
                "target_path": target_path,
                "type": type,
            }
        )
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if overwrite_existing is not UNSET:
            field_dict["overwrite_existing"] = overwrite_existing

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source = d.pop("source")

        source_type = DatasourceType(d.pop("source_type"))

        target_path = d.pop("target_path")

        type = d.pop("type")

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _overwrite_existing = d.pop("overwrite_existing", UNSET)
        overwrite_existing = (
            UNSET if _overwrite_existing is None else _overwrite_existing
        )

        obj = cls(
            source=source,
            source_type=source_type,
            target_path=target_path,
            type=type,
            data_connector_config_uid=data_connector_config_uid,
            dataset_uid=dataset_uid,
            overwrite_existing=overwrite_existing,
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
