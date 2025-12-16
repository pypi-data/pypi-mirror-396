from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.patch_node_response_node_config import (
        PatchNodeResponseNodeConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PatchNodeResponse")


@attrs.define
class PatchNodeResponse:
    """
    Attributes:
        node_config (PatchNodeResponseNodeConfig):
    """

    node_config: "PatchNodeResponseNodeConfig"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.patch_node_response_node_config import (
            PatchNodeResponseNodeConfig,  # noqa: F401
        )
        # fmt: on
        node_config = self.node_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_config": node_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.patch_node_response_node_config import (
            PatchNodeResponseNodeConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        node_config = PatchNodeResponseNodeConfig.from_dict(d.pop("node_config"))

        obj = cls(
            node_config=node_config,
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
