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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.prompt_execution import PromptExecution  # noqa: F401
    from ..models.prompt_fm_hyperparameters import PromptFmHyperparameters  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Prompt")


@attrs.define
class Prompt:
    """
    Attributes:
        created_at (datetime.datetime):
        created_by_user_uid (int):
        executions (List['PromptExecution']):
        prompt_uid (int):
        prompt_version_name (str):
        starred (bool):
        system_prompt_text (str):
        updated_at (datetime.datetime):
        user_prompt_text (str):
        workflow_uid (int):
        created_by_username (Union[Unset, str]):
        fm_hyperparameters (Union[Unset, PromptFmHyperparameters]):
        is_active_in_evaluator (Union[Unset, bool]):  Default: False.
        model_name (Union[Unset, str]):
        model_type (Union[Unset, str]):
    """

    created_at: datetime.datetime
    created_by_user_uid: int
    executions: List["PromptExecution"]
    prompt_uid: int
    prompt_version_name: str
    starred: bool
    system_prompt_text: str
    updated_at: datetime.datetime
    user_prompt_text: str
    workflow_uid: int
    created_by_username: Union[Unset, str] = UNSET
    fm_hyperparameters: Union[Unset, "PromptFmHyperparameters"] = UNSET
    is_active_in_evaluator: Union[Unset, bool] = False
    model_name: Union[Unset, str] = UNSET
    model_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_execution import PromptExecution  # noqa: F401
        from ..models.prompt_fm_hyperparameters import (
            PromptFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        created_at = self.created_at.isoformat()
        created_by_user_uid = self.created_by_user_uid
        executions = []
        for executions_item_data in self.executions:
            executions_item = executions_item_data.to_dict()
            executions.append(executions_item)

        prompt_uid = self.prompt_uid
        prompt_version_name = self.prompt_version_name
        starred = self.starred
        system_prompt_text = self.system_prompt_text
        updated_at = self.updated_at.isoformat()
        user_prompt_text = self.user_prompt_text
        workflow_uid = self.workflow_uid
        created_by_username = self.created_by_username
        fm_hyperparameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fm_hyperparameters, Unset):
            fm_hyperparameters = self.fm_hyperparameters.to_dict()
        is_active_in_evaluator = self.is_active_in_evaluator
        model_name = self.model_name
        model_type = self.model_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "created_by_user_uid": created_by_user_uid,
                "executions": executions,
                "prompt_uid": prompt_uid,
                "prompt_version_name": prompt_version_name,
                "starred": starred,
                "system_prompt_text": system_prompt_text,
                "updated_at": updated_at,
                "user_prompt_text": user_prompt_text,
                "workflow_uid": workflow_uid,
            }
        )
        if created_by_username is not UNSET:
            field_dict["created_by_username"] = created_by_username
        if fm_hyperparameters is not UNSET:
            field_dict["fm_hyperparameters"] = fm_hyperparameters
        if is_active_in_evaluator is not UNSET:
            field_dict["is_active_in_evaluator"] = is_active_in_evaluator
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if model_type is not UNSET:
            field_dict["model_type"] = model_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_execution import PromptExecution  # noqa: F401
        from ..models.prompt_fm_hyperparameters import (
            PromptFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        created_by_user_uid = d.pop("created_by_user_uid")

        executions = []
        _executions = d.pop("executions")
        for executions_item_data in _executions:
            executions_item = PromptExecution.from_dict(executions_item_data)

            executions.append(executions_item)

        prompt_uid = d.pop("prompt_uid")

        prompt_version_name = d.pop("prompt_version_name")

        starred = d.pop("starred")

        system_prompt_text = d.pop("system_prompt_text")

        updated_at = isoparse(d.pop("updated_at"))

        user_prompt_text = d.pop("user_prompt_text")

        workflow_uid = d.pop("workflow_uid")

        _created_by_username = d.pop("created_by_username", UNSET)
        created_by_username = (
            UNSET if _created_by_username is None else _created_by_username
        )

        _fm_hyperparameters = d.pop("fm_hyperparameters", UNSET)
        _fm_hyperparameters = (
            UNSET if _fm_hyperparameters is None else _fm_hyperparameters
        )
        fm_hyperparameters: Union[Unset, PromptFmHyperparameters]
        if isinstance(_fm_hyperparameters, Unset):
            fm_hyperparameters = UNSET
        else:
            fm_hyperparameters = PromptFmHyperparameters.from_dict(_fm_hyperparameters)

        _is_active_in_evaluator = d.pop("is_active_in_evaluator", UNSET)
        is_active_in_evaluator = (
            UNSET if _is_active_in_evaluator is None else _is_active_in_evaluator
        )

        _model_name = d.pop("model_name", UNSET)
        model_name = UNSET if _model_name is None else _model_name

        _model_type = d.pop("model_type", UNSET)
        model_type = UNSET if _model_type is None else _model_type

        obj = cls(
            created_at=created_at,
            created_by_user_uid=created_by_user_uid,
            executions=executions,
            prompt_uid=prompt_uid,
            prompt_version_name=prompt_version_name,
            starred=starred,
            system_prompt_text=system_prompt_text,
            updated_at=updated_at,
            user_prompt_text=user_prompt_text,
            workflow_uid=workflow_uid,
            created_by_username=created_by_username,
            fm_hyperparameters=fm_hyperparameters,
            is_active_in_evaluator=is_active_in_evaluator,
            model_name=model_name,
            model_type=model_type,
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
