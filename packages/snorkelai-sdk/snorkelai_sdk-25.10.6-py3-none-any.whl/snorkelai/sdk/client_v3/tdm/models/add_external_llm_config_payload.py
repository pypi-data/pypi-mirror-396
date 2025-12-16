from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.external_llm_provider import ExternalLLMProvider

if TYPE_CHECKING:
    # fmt: off
    from ..models.add_external_llm_config_payload_config import (
        AddExternalLLMConfigPayloadConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AddExternalLLMConfigPayload")


@attrs.define
class AddExternalLLMConfigPayload:
    """
    Attributes:
        config (AddExternalLLMConfigPayloadConfig):
        model_name (str):
        model_provider (ExternalLLMProvider):
        workspace_uid (int):
    """

    config: "AddExternalLLMConfigPayloadConfig"
    model_name: str
    model_provider: ExternalLLMProvider
    workspace_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.add_external_llm_config_payload_config import (
            AddExternalLLMConfigPayloadConfig,  # noqa: F401
        )
        # fmt: on
        config = self.config.to_dict()
        model_name = self.model_name
        model_provider = self.model_provider.value
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "model_name": model_name,
                "model_provider": model_provider,
                "workspace_uid": workspace_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.add_external_llm_config_payload_config import (
            AddExternalLLMConfigPayloadConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        config = AddExternalLLMConfigPayloadConfig.from_dict(d.pop("config"))

        model_name = d.pop("model_name")

        model_provider = ExternalLLMProvider(d.pop("model_provider"))

        workspace_uid = d.pop("workspace_uid")

        obj = cls(
            config=config,
            model_name=model_name,
            model_provider=model_provider,
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
