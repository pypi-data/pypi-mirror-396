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
    from ..models.create_new_prompt_version import CreateNewPromptVersion  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreatePromptEvaluatorForCriteriaPayload")


@attrs.define
class CreatePromptEvaluatorForCriteriaPayload:
    """
    Attributes:
        prompt_configuration (Union[Unset, CreateNewPromptVersion]):
    """

    prompt_configuration: Union[Unset, "CreateNewPromptVersion"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_new_prompt_version import (
            CreateNewPromptVersion,  # noqa: F401
        )
        # fmt: on
        prompt_configuration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prompt_configuration, Unset):
            prompt_configuration = self.prompt_configuration.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if prompt_configuration is not UNSET:
            field_dict["prompt_configuration"] = prompt_configuration

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_new_prompt_version import (
            CreateNewPromptVersion,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _prompt_configuration = d.pop("prompt_configuration", UNSET)
        _prompt_configuration = (
            UNSET if _prompt_configuration is None else _prompt_configuration
        )
        prompt_configuration: Union[Unset, CreateNewPromptVersion]
        if isinstance(_prompt_configuration, Unset):
            prompt_configuration = UNSET
        else:
            prompt_configuration = CreateNewPromptVersion.from_dict(
                _prompt_configuration
            )

        obj = cls(
            prompt_configuration=prompt_configuration,
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
