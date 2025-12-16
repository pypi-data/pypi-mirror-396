from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.prompt_lf_type import PromptLFType

if TYPE_CHECKING:
    # fmt: off
    from ..models.supported_llm import SupportedLLM  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetSupportedPromptBuilderModelsResponse")


@attrs.define
class GetSupportedPromptBuilderModelsResponse:
    """
    Attributes:
        prompt_lf_template_types (List[PromptLFType]):
        supported_models (List['SupportedLLM']):
    """

    prompt_lf_template_types: List[PromptLFType]
    supported_models: List["SupportedLLM"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.supported_llm import SupportedLLM  # noqa: F401
        # fmt: on
        prompt_lf_template_types = []
        for prompt_lf_template_types_item_data in self.prompt_lf_template_types:
            prompt_lf_template_types_item = prompt_lf_template_types_item_data.value
            prompt_lf_template_types.append(prompt_lf_template_types_item)

        supported_models = []
        for supported_models_item_data in self.supported_models:
            supported_models_item = supported_models_item_data.to_dict()
            supported_models.append(supported_models_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt_lf_template_types": prompt_lf_template_types,
                "supported_models": supported_models,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.supported_llm import SupportedLLM  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        prompt_lf_template_types = []
        _prompt_lf_template_types = d.pop("prompt_lf_template_types")
        for prompt_lf_template_types_item_data in _prompt_lf_template_types:
            prompt_lf_template_types_item = PromptLFType(
                prompt_lf_template_types_item_data
            )

            prompt_lf_template_types.append(prompt_lf_template_types_item)

        supported_models = []
        _supported_models = d.pop("supported_models")
        for supported_models_item_data in _supported_models:
            supported_models_item = SupportedLLM.from_dict(supported_models_item_data)

            supported_models.append(supported_models_item)

        obj = cls(
            prompt_lf_template_types=prompt_lf_template_types,
            supported_models=supported_models,
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
