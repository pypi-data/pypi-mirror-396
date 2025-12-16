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
    from ..models.prompt_to_response import PromptToResponse  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PromptDevExecutionXuidResponse")


@attrs.define
class PromptDevExecutionXuidResponse:
    """
    Attributes:
        prompts_to_responses (List['PromptToResponse']):
    """

    prompts_to_responses: List["PromptToResponse"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_to_response import PromptToResponse  # noqa: F401
        # fmt: on
        prompts_to_responses = []
        for prompts_to_responses_item_data in self.prompts_to_responses:
            prompts_to_responses_item = prompts_to_responses_item_data.to_dict()
            prompts_to_responses.append(prompts_to_responses_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompts_to_responses": prompts_to_responses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_to_response import PromptToResponse  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        prompts_to_responses = []
        _prompts_to_responses = d.pop("prompts_to_responses")
        for prompts_to_responses_item_data in _prompts_to_responses:
            prompts_to_responses_item = PromptToResponse.from_dict(
                prompts_to_responses_item_data
            )

            prompts_to_responses.append(prompts_to_responses_item)

        obj = cls(
            prompts_to_responses=prompts_to_responses,
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
