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
    from ..models.slice_config import SliceConfig  # noqa: F401
    from ..models.slice_with_config_metadata import (
        SliceWithConfigMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SliceWithConfig")


@attrs.define
class SliceWithConfig:
    """
    Attributes:
        config_updated_at (datetime.datetime):
        dataset_uid (int):
        display_name (str):
        slice_uid (int):
        updated_at (datetime.datetime):
        vds_uid (int):
        config (Union[Unset, SliceConfig]):
        description (Union[Unset, str]):
        metadata (Union[Unset, SliceWithConfigMetadata]):
        user_uid (Union[Unset, int]):
    """

    config_updated_at: datetime.datetime
    dataset_uid: int
    display_name: str
    slice_uid: int
    updated_at: datetime.datetime
    vds_uid: int
    config: Union[Unset, "SliceConfig"] = UNSET
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "SliceWithConfigMetadata"] = UNSET
    user_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.slice_config import SliceConfig  # noqa: F401
        from ..models.slice_with_config_metadata import (
            SliceWithConfigMetadata,  # noqa: F401
        )
        # fmt: on
        config_updated_at = self.config_updated_at.isoformat()
        dataset_uid = self.dataset_uid
        display_name = self.display_name
        slice_uid = self.slice_uid
        updated_at = self.updated_at.isoformat()
        vds_uid = self.vds_uid
        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()
        description = self.description
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        user_uid = self.user_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config_updated_at": config_updated_at,
                "dataset_uid": dataset_uid,
                "display_name": display_name,
                "slice_uid": slice_uid,
                "updated_at": updated_at,
                "vds_uid": vds_uid,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.slice_config import SliceConfig  # noqa: F401
        from ..models.slice_with_config_metadata import (
            SliceWithConfigMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        config_updated_at = isoparse(d.pop("config_updated_at"))

        dataset_uid = d.pop("dataset_uid")

        display_name = d.pop("display_name")

        slice_uid = d.pop("slice_uid")

        updated_at = isoparse(d.pop("updated_at"))

        vds_uid = d.pop("vds_uid")

        _config = d.pop("config", UNSET)
        _config = UNSET if _config is None else _config
        config: Union[Unset, SliceConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = SliceConfig.from_dict(_config)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, SliceWithConfigMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SliceWithConfigMetadata.from_dict(_metadata)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        obj = cls(
            config_updated_at=config_updated_at,
            dataset_uid=dataset_uid,
            display_name=display_name,
            slice_uid=slice_uid,
            updated_at=updated_at,
            vds_uid=vds_uid,
            config=config,
            description=description,
            metadata=metadata,
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
