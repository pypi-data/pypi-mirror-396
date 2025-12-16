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
    from ..models.prompt import Prompt  # noqa: F401
    from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreatePromptEvaluatorResponse")


@attrs.define
class CreatePromptEvaluatorResponse:
    """
    Attributes:
        prompt (Prompt):
        prompt_evaluator (PromptEvaluator):
    """

    prompt: "Prompt"
    prompt_evaluator: "PromptEvaluator"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt import Prompt  # noqa: F401
        from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
        # fmt: on
        prompt = self.prompt.to_dict()
        prompt_evaluator = self.prompt_evaluator.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt": prompt,
                "prompt_evaluator": prompt_evaluator,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt import Prompt  # noqa: F401
        from ..models.prompt_evaluator import PromptEvaluator  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        prompt = Prompt.from_dict(d.pop("prompt"))

        prompt_evaluator = PromptEvaluator.from_dict(d.pop("prompt_evaluator"))

        obj = cls(
            prompt=prompt,
            prompt_evaluator=prompt_evaluator,
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
