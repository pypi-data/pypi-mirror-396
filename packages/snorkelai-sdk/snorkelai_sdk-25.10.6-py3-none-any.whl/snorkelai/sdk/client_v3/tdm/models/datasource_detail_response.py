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
    from ..models.datasource_detail_response_config import (
        DatasourceDetailResponseConfig,  # noqa: F401
    )
    from ..models.datasource_detail_response_metadata import (
        DatasourceDetailResponseMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DatasourceDetailResponse")


@attrs.define
class DatasourceDetailResponse:
    """Response for retrieving a single datasource.

    Attributes:
        created_at (str):
        dataset_uid (int):
        datasource_uid (int):
        name (str):
        path (str):
        source_type (str):
        split (str):
        config (Union[Unset, DatasourceDetailResponseConfig]):
        metadata (Union[Unset, DatasourceDetailResponseMetadata]):
        modified_at (Union[Unset, str]):
    """

    created_at: str
    dataset_uid: int
    datasource_uid: int
    name: str
    path: str
    source_type: str
    split: str
    config: Union[Unset, "DatasourceDetailResponseConfig"] = UNSET
    metadata: Union[Unset, "DatasourceDetailResponseMetadata"] = UNSET
    modified_at: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.datasource_detail_response_config import (
            DatasourceDetailResponseConfig,  # noqa: F401
        )
        from ..models.datasource_detail_response_metadata import (
            DatasourceDetailResponseMetadata,  # noqa: F401
        )
        # fmt: on
        created_at = self.created_at
        dataset_uid = self.dataset_uid
        datasource_uid = self.datasource_uid
        name = self.name
        path = self.path
        source_type = self.source_type
        split = self.split
        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        modified_at = self.modified_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "dataset_uid": dataset_uid,
                "datasource_uid": datasource_uid,
                "name": name,
                "path": path,
                "source_type": source_type,
                "split": split,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if modified_at is not UNSET:
            field_dict["modified_at"] = modified_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.datasource_detail_response_config import (
            DatasourceDetailResponseConfig,  # noqa: F401
        )
        from ..models.datasource_detail_response_metadata import (
            DatasourceDetailResponseMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_at = d.pop("created_at")

        dataset_uid = d.pop("dataset_uid")

        datasource_uid = d.pop("datasource_uid")

        name = d.pop("name")

        path = d.pop("path")

        source_type = d.pop("source_type")

        split = d.pop("split")

        _config = d.pop("config", UNSET)
        _config = UNSET if _config is None else _config
        config: Union[Unset, DatasourceDetailResponseConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = DatasourceDetailResponseConfig.from_dict(_config)

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, DatasourceDetailResponseMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DatasourceDetailResponseMetadata.from_dict(_metadata)

        _modified_at = d.pop("modified_at", UNSET)
        modified_at = UNSET if _modified_at is None else _modified_at

        obj = cls(
            created_at=created_at,
            dataset_uid=dataset_uid,
            datasource_uid=datasource_uid,
            name=name,
            path=path,
            source_type=source_type,
            split=split,
            config=config,
            metadata=metadata,
            modified_at=modified_at,
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
