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
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.save_prompt_as_template_request_hyperparameters import (
        SavePromptAsTemplateRequestHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SavePromptAsTemplateRequest")


@attrs.define
class SavePromptAsTemplateRequest:
    """
    Attributes:
        hyperparameters (SavePromptAsTemplateRequestHyperparameters):
        model (str):
        prompt_template_description (str):
        prompt_template_name (str):
        source_prompt_version_uid (int):
        system_prompt (str):
        user_prompt (str):
        origin (Union[Unset, PromptTemplateOrigin]):
    """

    hyperparameters: "SavePromptAsTemplateRequestHyperparameters"
    model: str
    prompt_template_description: str
    prompt_template_name: str
    source_prompt_version_uid: int
    system_prompt: str
    user_prompt: str
    origin: Union[Unset, PromptTemplateOrigin] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.save_prompt_as_template_request_hyperparameters import (
            SavePromptAsTemplateRequestHyperparameters,  # noqa: F401
        )
        # fmt: on
        hyperparameters = self.hyperparameters.to_dict()
        model = self.model
        prompt_template_description = self.prompt_template_description
        prompt_template_name = self.prompt_template_name
        source_prompt_version_uid = self.source_prompt_version_uid
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt
        origin: Union[Unset, str] = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hyperparameters": hyperparameters,
                "model": model,
                "prompt_template_description": prompt_template_description,
                "prompt_template_name": prompt_template_name,
                "source_prompt_version_uid": source_prompt_version_uid,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            }
        )
        if origin is not UNSET:
            field_dict["origin"] = origin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.save_prompt_as_template_request_hyperparameters import (
            SavePromptAsTemplateRequestHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        hyperparameters = SavePromptAsTemplateRequestHyperparameters.from_dict(
            d.pop("hyperparameters")
        )

        model = d.pop("model")

        prompt_template_description = d.pop("prompt_template_description")

        prompt_template_name = d.pop("prompt_template_name")

        source_prompt_version_uid = d.pop("source_prompt_version_uid")

        system_prompt = d.pop("system_prompt")

        user_prompt = d.pop("user_prompt")

        _origin = d.pop("origin", UNSET)
        _origin = UNSET if _origin is None else _origin
        origin: Union[Unset, PromptTemplateOrigin]
        if isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = PromptTemplateOrigin(_origin)

        obj = cls(
            hyperparameters=hyperparameters,
            model=model,
            prompt_template_description=prompt_template_description,
            prompt_template_name=prompt_template_name,
            source_prompt_version_uid=source_prompt_version_uid,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            origin=origin,
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
