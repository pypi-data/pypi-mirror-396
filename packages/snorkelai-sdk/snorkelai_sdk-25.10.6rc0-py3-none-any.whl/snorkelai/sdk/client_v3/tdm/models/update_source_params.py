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
    from ..models.update_source_params_metadata import (
        UpdateSourceParamsMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdateSourceParams")


@attrs.define
class UpdateSourceParams:
    """
    Attributes:
        metadata (Union[Unset, UpdateSourceParamsMetadata]):
        source_name (Union[Unset, str]):
    """

    metadata: Union[Unset, "UpdateSourceParamsMetadata"] = UNSET
    source_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_source_params_metadata import (
            UpdateSourceParamsMetadata,  # noqa: F401
        )
        # fmt: on
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        source_name = self.source_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if source_name is not UNSET:
            field_dict["source_name"] = source_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_source_params_metadata import (
            UpdateSourceParamsMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, UpdateSourceParamsMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateSourceParamsMetadata.from_dict(_metadata)

        _source_name = d.pop("source_name", UNSET)
        source_name = UNSET if _source_name is None else _source_name

        obj = cls(
            metadata=metadata,
            source_name=source_name,
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
