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
    from ..models.create_op_version_payload_op_config import (
        CreateOpVersionPayloadOpConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateOpVersionPayload")


@attrs.define
class CreateOpVersionPayload:
    """
    Attributes:
        op_config (CreateOpVersionPayloadOpConfig):
        op_type (str):
        op_name (Union[Unset, str]):
    """

    op_config: "CreateOpVersionPayloadOpConfig"
    op_type: str
    op_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_op_version_payload_op_config import (
            CreateOpVersionPayloadOpConfig,  # noqa: F401
        )
        # fmt: on
        op_config = self.op_config.to_dict()
        op_type = self.op_type
        op_name = self.op_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "op_config": op_config,
                "op_type": op_type,
            }
        )
        if op_name is not UNSET:
            field_dict["op_name"] = op_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_op_version_payload_op_config import (
            CreateOpVersionPayloadOpConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        op_config = CreateOpVersionPayloadOpConfig.from_dict(d.pop("op_config"))

        op_type = d.pop("op_type")

        _op_name = d.pop("op_name", UNSET)
        op_name = UNSET if _op_name is None else _op_name

        obj = cls(
            op_config=op_config,
            op_type=op_type,
            op_name=op_name,
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
