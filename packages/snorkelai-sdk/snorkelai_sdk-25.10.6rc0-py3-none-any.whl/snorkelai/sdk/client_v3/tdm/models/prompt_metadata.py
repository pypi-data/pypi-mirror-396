import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs
from dateutil.parser import isoparse

if TYPE_CHECKING:
    # fmt: off
    from ..models.prompt_metadata_fm_hyperparameters import (
        PromptMetadataFmHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptMetadata")


@attrs.define
class PromptMetadata:
    """
    Attributes:
        created_at (datetime.datetime):
        created_by_user_uid (int):
        fm_hyperparameters (PromptMetadataFmHyperparameters):
        model_name (str):
        model_type (str):
        prompt_execution_uid (int):
        prompt_uid (int):
        prompt_version_name (str):
        starred (bool):
        system_prompt_text (str):
        user_prompt_text (str):
        workflow_uid (int):
    """

    created_at: datetime.datetime
    created_by_user_uid: int
    fm_hyperparameters: "PromptMetadataFmHyperparameters"
    model_name: str
    model_type: str
    prompt_execution_uid: int
    prompt_uid: int
    prompt_version_name: str
    starred: bool
    system_prompt_text: str
    user_prompt_text: str
    workflow_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_metadata_fm_hyperparameters import (
            PromptMetadataFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        created_at = self.created_at.isoformat()
        created_by_user_uid = self.created_by_user_uid
        fm_hyperparameters = self.fm_hyperparameters.to_dict()
        model_name = self.model_name
        model_type = self.model_type
        prompt_execution_uid = self.prompt_execution_uid
        prompt_uid = self.prompt_uid
        prompt_version_name = self.prompt_version_name
        starred = self.starred
        system_prompt_text = self.system_prompt_text
        user_prompt_text = self.user_prompt_text
        workflow_uid = self.workflow_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "created_by_user_uid": created_by_user_uid,
                "fm_hyperparameters": fm_hyperparameters,
                "model_name": model_name,
                "model_type": model_type,
                "prompt_execution_uid": prompt_execution_uid,
                "prompt_uid": prompt_uid,
                "prompt_version_name": prompt_version_name,
                "starred": starred,
                "system_prompt_text": system_prompt_text,
                "user_prompt_text": user_prompt_text,
                "workflow_uid": workflow_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_metadata_fm_hyperparameters import (
            PromptMetadataFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        created_by_user_uid = d.pop("created_by_user_uid")

        fm_hyperparameters = PromptMetadataFmHyperparameters.from_dict(
            d.pop("fm_hyperparameters")
        )

        model_name = d.pop("model_name")

        model_type = d.pop("model_type")

        prompt_execution_uid = d.pop("prompt_execution_uid")

        prompt_uid = d.pop("prompt_uid")

        prompt_version_name = d.pop("prompt_version_name")

        starred = d.pop("starred")

        system_prompt_text = d.pop("system_prompt_text")

        user_prompt_text = d.pop("user_prompt_text")

        workflow_uid = d.pop("workflow_uid")

        obj = cls(
            created_at=created_at,
            created_by_user_uid=created_by_user_uid,
            fm_hyperparameters=fm_hyperparameters,
            model_name=model_name,
            model_type=model_type,
            prompt_execution_uid=prompt_execution_uid,
            prompt_uid=prompt_uid,
            prompt_version_name=prompt_version_name,
            starred=starred,
            system_prompt_text=system_prompt_text,
            user_prompt_text=user_prompt_text,
            workflow_uid=workflow_uid,
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
