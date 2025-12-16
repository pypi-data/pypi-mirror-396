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
    from ..models.extractor_config_op_config import (
        ExtractorConfigOpConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ExtractorConfig")


@attrs.define
class ExtractorConfig:
    """
    Attributes:
        op_config (ExtractorConfigOpConfig):
        op_type (str):
    """

    op_config: "ExtractorConfigOpConfig"
    op_type: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.extractor_config_op_config import (
            ExtractorConfigOpConfig,  # noqa: F401
        )
        # fmt: on
        op_config = self.op_config.to_dict()
        op_type = self.op_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "op_config": op_config,
                "op_type": op_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.extractor_config_op_config import (
            ExtractorConfigOpConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        op_config = ExtractorConfigOpConfig.from_dict(d.pop("op_config"))

        op_type = d.pop("op_type")

        obj = cls(
            op_config=op_config,
            op_type=op_type,
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
