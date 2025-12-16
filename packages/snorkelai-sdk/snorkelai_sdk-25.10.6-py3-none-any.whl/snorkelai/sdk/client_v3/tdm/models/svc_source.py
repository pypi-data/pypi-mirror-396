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

from ..models.svc_source_type import SvcSourceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.svc_source_metadata import SvcSourceMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SvcSource")


@attrs.define
class SvcSource:
    """
    Attributes:
        source_name (str):
        source_type (SvcSourceType):
        source_uid (int):
        metadata (Union[Unset, SvcSourceMetadata]):
        user_uid (Union[Unset, int]):
        workspace_uid (Union[Unset, int]):  Default: 1.
    """

    source_name: str
    source_type: SvcSourceType
    source_uid: int
    metadata: Union[Unset, "SvcSourceMetadata"] = UNSET
    user_uid: Union[Unset, int] = UNSET
    workspace_uid: Union[Unset, int] = 1
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.svc_source_metadata import SvcSourceMetadata  # noqa: F401
        # fmt: on
        source_name = self.source_name
        source_type = self.source_type.value
        source_uid = self.source_uid
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        user_uid = self.user_uid
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_name": source_name,
                "source_type": source_type,
                "source_uid": source_uid,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.svc_source_metadata import SvcSourceMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        source_name = d.pop("source_name")

        source_type = SvcSourceType(d.pop("source_type"))

        source_uid = d.pop("source_uid")

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, SvcSourceMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SvcSourceMetadata.from_dict(_metadata)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            source_name=source_name,
            source_type=source_type,
            source_uid=source_uid,
            metadata=metadata,
            user_uid=user_uid,
            workspace_uid=workspace_uid,
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
