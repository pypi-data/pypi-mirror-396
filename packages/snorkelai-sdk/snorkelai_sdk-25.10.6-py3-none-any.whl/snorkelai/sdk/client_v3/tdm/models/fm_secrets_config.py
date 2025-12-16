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

if TYPE_CHECKING:
    # fmt: off
    from ..models.anthropic_secrets_config import AnthropicSecretsConfig  # noqa: F401
    from ..models.azure_ml_secrets_config import AzureMLSecretsConfig  # noqa: F401
    from ..models.azure_open_ai_secrets_config import (
        AzureOpenAISecretsConfig,  # noqa: F401
    )
    from ..models.bedrock_secrets_config import BedrockSecretsConfig  # noqa: F401
    from ..models.custom_inference_service_secrets_config import (
        CustomInferenceServiceSecretsConfig,  # noqa: F401
    )
    from ..models.hugging_face_secrets_config import (
        HuggingFaceSecretsConfig,  # noqa: F401
    )
    from ..models.open_ai_secrets_config import OpenAISecretsConfig  # noqa: F401
    from ..models.vertex_ai_secrets_config import VertexAISecretsConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FMSecretsConfig")


@attrs.define
class FMSecretsConfig:
    """
    Attributes:
        fm_secrets_config (Union['AnthropicSecretsConfig', 'AzureMLSecretsConfig', 'AzureOpenAISecretsConfig',
            'BedrockSecretsConfig', 'CustomInferenceServiceSecretsConfig', 'HuggingFaceSecretsConfig',
            'OpenAISecretsConfig', 'VertexAISecretsConfig']):
    """

    fm_secrets_config: Union[
        "AnthropicSecretsConfig",
        "AzureMLSecretsConfig",
        "AzureOpenAISecretsConfig",
        "BedrockSecretsConfig",
        "CustomInferenceServiceSecretsConfig",
        "HuggingFaceSecretsConfig",
        "OpenAISecretsConfig",
        "VertexAISecretsConfig",
    ]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.anthropic_secrets_config import (
            AnthropicSecretsConfig,  # noqa: F401
        )
        from ..models.azure_ml_secrets_config import AzureMLSecretsConfig  # noqa: F401
        from ..models.azure_open_ai_secrets_config import (
            AzureOpenAISecretsConfig,  # noqa: F401
        )
        from ..models.bedrock_secrets_config import BedrockSecretsConfig  # noqa: F401
        from ..models.custom_inference_service_secrets_config import (
            CustomInferenceServiceSecretsConfig,  # noqa: F401
        )
        from ..models.hugging_face_secrets_config import (
            HuggingFaceSecretsConfig,  # noqa: F401
        )
        from ..models.open_ai_secrets_config import OpenAISecretsConfig  # noqa: F401
        from ..models.vertex_ai_secrets_config import (
            VertexAISecretsConfig,  # noqa: F401
        )
        # fmt: on
        fm_secrets_config: Dict[str, Any]
        if isinstance(self.fm_secrets_config, AnthropicSecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, AzureMLSecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, AzureOpenAISecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, BedrockSecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, CustomInferenceServiceSecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, HuggingFaceSecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        elif isinstance(self.fm_secrets_config, OpenAISecretsConfig):
            fm_secrets_config = self.fm_secrets_config.to_dict()
        else:
            fm_secrets_config = self.fm_secrets_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fm_secrets_config": fm_secrets_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.anthropic_secrets_config import (
            AnthropicSecretsConfig,  # noqa: F401
        )
        from ..models.azure_ml_secrets_config import AzureMLSecretsConfig  # noqa: F401
        from ..models.azure_open_ai_secrets_config import (
            AzureOpenAISecretsConfig,  # noqa: F401
        )
        from ..models.bedrock_secrets_config import BedrockSecretsConfig  # noqa: F401
        from ..models.custom_inference_service_secrets_config import (
            CustomInferenceServiceSecretsConfig,  # noqa: F401
        )
        from ..models.hugging_face_secrets_config import (
            HuggingFaceSecretsConfig,  # noqa: F401
        )
        from ..models.open_ai_secrets_config import OpenAISecretsConfig  # noqa: F401
        from ..models.vertex_ai_secrets_config import (
            VertexAISecretsConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()

        def _parse_fm_secrets_config(
            data: object,
        ) -> Union[
            "AnthropicSecretsConfig",
            "AzureMLSecretsConfig",
            "AzureOpenAISecretsConfig",
            "BedrockSecretsConfig",
            "CustomInferenceServiceSecretsConfig",
            "HuggingFaceSecretsConfig",
            "OpenAISecretsConfig",
            "VertexAISecretsConfig",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_0 = AnthropicSecretsConfig.from_dict(data)

                return fm_secrets_config_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_1 = AzureMLSecretsConfig.from_dict(data)

                return fm_secrets_config_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_2 = AzureOpenAISecretsConfig.from_dict(data)

                return fm_secrets_config_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_3 = BedrockSecretsConfig.from_dict(data)

                return fm_secrets_config_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_4 = (
                    CustomInferenceServiceSecretsConfig.from_dict(data)
                )

                return fm_secrets_config_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_5 = HuggingFaceSecretsConfig.from_dict(data)

                return fm_secrets_config_type_5
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                fm_secrets_config_type_6 = OpenAISecretsConfig.from_dict(data)

                return fm_secrets_config_type_6
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            fm_secrets_config_type_7 = VertexAISecretsConfig.from_dict(data)

            return fm_secrets_config_type_7

        fm_secrets_config = _parse_fm_secrets_config(d.pop("fm_secrets_config"))

        obj = cls(
            fm_secrets_config=fm_secrets_config,
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
