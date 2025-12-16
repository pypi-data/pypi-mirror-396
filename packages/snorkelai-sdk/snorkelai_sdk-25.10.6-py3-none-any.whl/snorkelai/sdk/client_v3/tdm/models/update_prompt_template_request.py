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

from ..models.prompt_template_origin import PromptTemplateOrigin
from ..models.prompt_template_state import PromptTemplateState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.update_prompt_template_request_hyperparameters import (
        UpdatePromptTemplateRequestHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdatePromptTemplateRequest")


@attrs.define
class UpdatePromptTemplateRequest:
    """
    Attributes:
        hyperparameters (Union[Unset, UpdatePromptTemplateRequestHyperparameters]):
        model (Union[Unset, str]):
        origin (Union[Unset, PromptTemplateOrigin]):
        prompt_template_description (Union[Unset, str]):
        prompt_template_name (Union[Unset, str]):
        state (Union[Unset, PromptTemplateState]):
        system_prompt (Union[Unset, str]):
        user_prompt (Union[Unset, str]):
    """

    hyperparameters: Union[Unset, "UpdatePromptTemplateRequestHyperparameters"] = UNSET
    model: Union[Unset, str] = UNSET
    origin: Union[Unset, PromptTemplateOrigin] = UNSET
    prompt_template_description: Union[Unset, str] = UNSET
    prompt_template_name: Union[Unset, str] = UNSET
    state: Union[Unset, PromptTemplateState] = UNSET
    system_prompt: Union[Unset, str] = UNSET
    user_prompt: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_prompt_template_request_hyperparameters import (
            UpdatePromptTemplateRequestHyperparameters,  # noqa: F401
        )
        # fmt: on
        hyperparameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.hyperparameters, Unset):
            hyperparameters = self.hyperparameters.to_dict()
        model = self.model
        origin: Union[Unset, str] = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.value

        prompt_template_description = self.prompt_template_description
        prompt_template_name = self.prompt_template_name
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        system_prompt = self.system_prompt
        user_prompt = self.user_prompt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hyperparameters is not UNSET:
            field_dict["hyperparameters"] = hyperparameters
        if model is not UNSET:
            field_dict["model"] = model
        if origin is not UNSET:
            field_dict["origin"] = origin
        if prompt_template_description is not UNSET:
            field_dict["prompt_template_description"] = prompt_template_description
        if prompt_template_name is not UNSET:
            field_dict["prompt_template_name"] = prompt_template_name
        if state is not UNSET:
            field_dict["state"] = state
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if user_prompt is not UNSET:
            field_dict["user_prompt"] = user_prompt

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_prompt_template_request_hyperparameters import (
            UpdatePromptTemplateRequestHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _hyperparameters = d.pop("hyperparameters", UNSET)
        _hyperparameters = UNSET if _hyperparameters is None else _hyperparameters
        hyperparameters: Union[Unset, UpdatePromptTemplateRequestHyperparameters]
        if isinstance(_hyperparameters, Unset):
            hyperparameters = UNSET
        else:
            hyperparameters = UpdatePromptTemplateRequestHyperparameters.from_dict(
                _hyperparameters
            )

        _model = d.pop("model", UNSET)
        model = UNSET if _model is None else _model

        _origin = d.pop("origin", UNSET)
        _origin = UNSET if _origin is None else _origin
        origin: Union[Unset, PromptTemplateOrigin]
        if isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = PromptTemplateOrigin(_origin)

        _prompt_template_description = d.pop("prompt_template_description", UNSET)
        prompt_template_description = (
            UNSET
            if _prompt_template_description is None
            else _prompt_template_description
        )

        _prompt_template_name = d.pop("prompt_template_name", UNSET)
        prompt_template_name = (
            UNSET if _prompt_template_name is None else _prompt_template_name
        )

        _state = d.pop("state", UNSET)
        _state = UNSET if _state is None else _state
        state: Union[Unset, PromptTemplateState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = PromptTemplateState(_state)

        _system_prompt = d.pop("system_prompt", UNSET)
        system_prompt = UNSET if _system_prompt is None else _system_prompt

        _user_prompt = d.pop("user_prompt", UNSET)
        user_prompt = UNSET if _user_prompt is None else _user_prompt

        obj = cls(
            hyperparameters=hyperparameters,
            model=model,
            origin=origin,
            prompt_template_description=prompt_template_description,
            prompt_template_name=prompt_template_name,
            state=state,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
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
