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
    from ..models.patch_node_payload_patch_node_config import (
        PatchNodePayloadPatchNodeConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PatchNodePayload")


@attrs.define
class PatchNodePayload:
    """
    Attributes:
        patch_node_config (Union[Unset, PatchNodePayloadPatchNodeConfig]):
    """

    patch_node_config: Union[Unset, "PatchNodePayloadPatchNodeConfig"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.patch_node_payload_patch_node_config import (
            PatchNodePayloadPatchNodeConfig,  # noqa: F401
        )
        # fmt: on
        patch_node_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.patch_node_config, Unset):
            patch_node_config = self.patch_node_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if patch_node_config is not UNSET:
            field_dict["patch_node_config"] = patch_node_config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.patch_node_payload_patch_node_config import (
            PatchNodePayloadPatchNodeConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _patch_node_config = d.pop("patch_node_config", UNSET)
        _patch_node_config = UNSET if _patch_node_config is None else _patch_node_config
        patch_node_config: Union[Unset, PatchNodePayloadPatchNodeConfig]
        if isinstance(_patch_node_config, Unset):
            patch_node_config = UNSET
        else:
            patch_node_config = PatchNodePayloadPatchNodeConfig.from_dict(
                _patch_node_config
            )

        obj = cls(
            patch_node_config=patch_node_config,
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
