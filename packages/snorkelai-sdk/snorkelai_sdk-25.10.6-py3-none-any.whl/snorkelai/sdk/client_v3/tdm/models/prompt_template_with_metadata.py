import datetime
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
from dateutil.parser import isoparse

from ..models.prompt_template_origin import PromptTemplateOrigin
from ..models.prompt_template_state import PromptTemplateState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.prompt_template_with_metadata_hyperparameters import (
        PromptTemplateWithMetadataHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptTemplateWithMetadata")


@attrs.define
class PromptTemplateWithMetadata:
    """
    Attributes:
        created_by (int):
        hyperparameters (PromptTemplateWithMetadataHyperparameters):
        model (str):
        origin (PromptTemplateOrigin):
        prompt_template_description (str):
        prompt_template_name (str):
        source_prompt_version_name (str):
        source_prompt_version_uid (int):
        source_prompt_workflow_name (str):
        state (PromptTemplateState):
        system_prompt (str):
        user_prompt (str):
        workspace_uid (int):
        created_at (Union[Unset, datetime.datetime]):
        prompt_template_uid (Union[Unset, int]):
    """

    created_by: int
    hyperparameters: "PromptTemplateWithMetadataHyperparameters"
    model: str
    origin: PromptTemplateOrigin
    prompt_template_description: str
    prompt_template_name: str
    source_prompt_version_name: str
    source_prompt_version_uid: int
    source_prompt_workflow_name: str
    state: PromptTemplateState
    system_prompt: str
    user_prompt: str
    workspace_uid: int
    created_at: Union[Unset, datetime.datetime] = UNSET
    prompt_template_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_template_with_metadata_hyperparameters import (
            PromptTemplateWithMetadataHyperparameters,  # noqa: F401
        )
        # fmt: on
        created_by = self.created_by
        hyperparameters = self.hyperparameters.to_dict()
        model = self.model
        origin = self.origin.value
        prompt_template_description = self.prompt_template_description
        prompt_template_name = self.prompt_template_name
        source_prompt_version_name = self.source_prompt_version_name
        source_prompt_version_uid = self.source_prompt_version_uid
        source_prompt_workflow_name = self.source_prompt_workflow_name
        state = self.state.value
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt
        workspace_uid = self.workspace_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        prompt_template_uid = self.prompt_template_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_by": created_by,
                "hyperparameters": hyperparameters,
                "model": model,
                "origin": origin,
                "prompt_template_description": prompt_template_description,
                "prompt_template_name": prompt_template_name,
                "source_prompt_version_name": source_prompt_version_name,
                "source_prompt_version_uid": source_prompt_version_uid,
                "source_prompt_workflow_name": source_prompt_workflow_name,
                "state": state,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "workspace_uid": workspace_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if prompt_template_uid is not UNSET:
            field_dict["prompt_template_uid"] = prompt_template_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_template_with_metadata_hyperparameters import (
            PromptTemplateWithMetadataHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_by = d.pop("created_by")

        hyperparameters = PromptTemplateWithMetadataHyperparameters.from_dict(
            d.pop("hyperparameters")
        )

        model = d.pop("model")

        origin = PromptTemplateOrigin(d.pop("origin"))

        prompt_template_description = d.pop("prompt_template_description")

        prompt_template_name = d.pop("prompt_template_name")

        source_prompt_version_name = d.pop("source_prompt_version_name")

        source_prompt_version_uid = d.pop("source_prompt_version_uid")

        source_prompt_workflow_name = d.pop("source_prompt_workflow_name")

        state = PromptTemplateState(d.pop("state"))

        system_prompt = d.pop("system_prompt")

        user_prompt = d.pop("user_prompt")

        workspace_uid = d.pop("workspace_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _prompt_template_uid = d.pop("prompt_template_uid", UNSET)
        prompt_template_uid = (
            UNSET if _prompt_template_uid is None else _prompt_template_uid
        )

        obj = cls(
            created_by=created_by,
            hyperparameters=hyperparameters,
            model=model,
            origin=origin,
            prompt_template_description=prompt_template_description,
            prompt_template_name=prompt_template_name,
            source_prompt_version_name=source_prompt_version_name,
            source_prompt_version_uid=source_prompt_version_uid,
            source_prompt_workflow_name=source_prompt_workflow_name,
            state=state,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            workspace_uid=workspace_uid,
            created_at=created_at,
            prompt_template_uid=prompt_template_uid,
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
