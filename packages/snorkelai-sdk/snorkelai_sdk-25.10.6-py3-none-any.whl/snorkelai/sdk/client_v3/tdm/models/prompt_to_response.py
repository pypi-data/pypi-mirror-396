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
    from ..models.llm_response import LLMResponse  # noqa: F401
    from ..models.prompt_metadata import PromptMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PromptToResponse")


@attrs.define
class PromptToResponse:
    """
    Attributes:
        prompt (PromptMetadata):
        response (LLMResponse):
    """

    prompt: "PromptMetadata"
    response: "LLMResponse"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.llm_response import LLMResponse  # noqa: F401
        from ..models.prompt_metadata import PromptMetadata  # noqa: F401
        # fmt: on
        prompt = self.prompt.to_dict()
        response = self.response.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt": prompt,
                "response": response,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.llm_response import LLMResponse  # noqa: F401
        from ..models.prompt_metadata import PromptMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        prompt = PromptMetadata.from_dict(d.pop("prompt"))

        response = LLMResponse.from_dict(d.pop("response"))

        obj = cls(
            prompt=prompt,
            response=response,
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
