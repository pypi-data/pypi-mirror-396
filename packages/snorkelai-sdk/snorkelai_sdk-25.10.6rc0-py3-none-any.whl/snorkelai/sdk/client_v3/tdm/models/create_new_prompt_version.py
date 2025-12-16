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
    from ..models.create_new_prompt_version_fm_hyperparameters import (
        CreateNewPromptVersionFmHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateNewPromptVersion")


@attrs.define
class CreateNewPromptVersion:
    """
    Attributes:
        fm_hyperparameters (Union[Unset, CreateNewPromptVersionFmHyperparameters]):
        model_name (Union[Unset, str]):
        prompt_version_name (Union[Unset, str]):
        system_prompt (Union[Unset, str]):
        user_prompt (Union[Unset, str]):
    """

    fm_hyperparameters: Union[Unset, "CreateNewPromptVersionFmHyperparameters"] = UNSET
    model_name: Union[Unset, str] = UNSET
    prompt_version_name: Union[Unset, str] = UNSET
    system_prompt: Union[Unset, str] = UNSET
    user_prompt: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_new_prompt_version_fm_hyperparameters import (
            CreateNewPromptVersionFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        fm_hyperparameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fm_hyperparameters, Unset):
            fm_hyperparameters = self.fm_hyperparameters.to_dict()
        model_name = self.model_name
        prompt_version_name = self.prompt_version_name
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fm_hyperparameters is not UNSET:
            field_dict["fm_hyperparameters"] = fm_hyperparameters
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if prompt_version_name is not UNSET:
            field_dict["prompt_version_name"] = prompt_version_name
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if user_prompt is not UNSET:
            field_dict["user_prompt"] = user_prompt

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_new_prompt_version_fm_hyperparameters import (
            CreateNewPromptVersionFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _fm_hyperparameters = d.pop("fm_hyperparameters", UNSET)
        _fm_hyperparameters = (
            UNSET if _fm_hyperparameters is None else _fm_hyperparameters
        )
        fm_hyperparameters: Union[Unset, CreateNewPromptVersionFmHyperparameters]
        if isinstance(_fm_hyperparameters, Unset):
            fm_hyperparameters = UNSET
        else:
            fm_hyperparameters = CreateNewPromptVersionFmHyperparameters.from_dict(
                _fm_hyperparameters
            )

        _model_name = d.pop("model_name", UNSET)
        model_name = UNSET if _model_name is None else _model_name

        _prompt_version_name = d.pop("prompt_version_name", UNSET)
        prompt_version_name = (
            UNSET if _prompt_version_name is None else _prompt_version_name
        )

        _system_prompt = d.pop("system_prompt", UNSET)
        system_prompt = UNSET if _system_prompt is None else _system_prompt

        _user_prompt = d.pop("user_prompt", UNSET)
        user_prompt = UNSET if _user_prompt is None else _user_prompt

        obj = cls(
            fm_hyperparameters=fm_hyperparameters,
            model_name=model_name,
            prompt_version_name=prompt_version_name,
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
