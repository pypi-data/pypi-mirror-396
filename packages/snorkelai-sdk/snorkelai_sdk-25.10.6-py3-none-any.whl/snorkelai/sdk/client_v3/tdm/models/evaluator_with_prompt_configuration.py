import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..models.evaluator_type import EvaluatorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EvaluatorWithPromptConfiguration")


@attrs.define
class EvaluatorWithPromptConfiguration:
    """
    Attributes:
        criteria_uid (int):
        evaluator_uid (int):
        model_name (str):
        name (str):
        system_prompt_text (str):
        type (EvaluatorType):
        user_prompt_text (str):
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    criteria_uid: int
    evaluator_uid: int
    model_name: str
    name: str
    system_prompt_text: str
    type: EvaluatorType
    user_prompt_text: str
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        criteria_uid = self.criteria_uid
        evaluator_uid = self.evaluator_uid
        model_name = self.model_name
        name = self.name
        system_prompt_text = self.system_prompt_text
        type = self.type.value
        user_prompt_text = self.user_prompt_text
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_uid": criteria_uid,
                "evaluator_uid": evaluator_uid,
                "model_name": model_name,
                "name": name,
                "system_prompt_text": system_prompt_text,
                "type": type,
                "user_prompt_text": user_prompt_text,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        criteria_uid = d.pop("criteria_uid")

        evaluator_uid = d.pop("evaluator_uid")

        model_name = d.pop("model_name")

        name = d.pop("name")

        system_prompt_text = d.pop("system_prompt_text")

        type = EvaluatorType(d.pop("type"))

        user_prompt_text = d.pop("user_prompt_text")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            criteria_uid=criteria_uid,
            evaluator_uid=evaluator_uid,
            model_name=model_name,
            name=name,
            system_prompt_text=system_prompt_text,
            type=type,
            user_prompt_text=user_prompt_text,
            created_at=created_at,
            description=description,
            updated_at=updated_at,
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
