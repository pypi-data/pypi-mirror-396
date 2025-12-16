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

T = TypeVar("T", bound="CodeEvaluator")


@attrs.define
class CodeEvaluator:
    """
    Attributes:
        code_version_uid (int):
        code_workflow_uid (int):
        criteria_uid (int):
        evaluator_uid (int):
        name (str):
        code_execution_uid (Union[Unset, int]):
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        type (Union[Unset, EvaluatorType]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    code_version_uid: int
    code_workflow_uid: int
    criteria_uid: int
    evaluator_uid: int
    name: str
    code_execution_uid: Union[Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    type: Union[Unset, EvaluatorType] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code_version_uid = self.code_version_uid
        code_workflow_uid = self.code_workflow_uid
        criteria_uid = self.criteria_uid
        evaluator_uid = self.evaluator_uid
        name = self.name
        code_execution_uid = self.code_execution_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code_version_uid": code_version_uid,
                "code_workflow_uid": code_workflow_uid,
                "criteria_uid": criteria_uid,
                "evaluator_uid": evaluator_uid,
                "name": name,
            }
        )
        if code_execution_uid is not UNSET:
            field_dict["code_execution_uid"] = code_execution_uid
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if type is not UNSET:
            field_dict["type"] = type
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code_version_uid = d.pop("code_version_uid")

        code_workflow_uid = d.pop("code_workflow_uid")

        criteria_uid = d.pop("criteria_uid")

        evaluator_uid = d.pop("evaluator_uid")

        name = d.pop("name")

        _code_execution_uid = d.pop("code_execution_uid", UNSET)
        code_execution_uid = (
            UNSET if _code_execution_uid is None else _code_execution_uid
        )

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _type = d.pop("type", UNSET)
        _type = UNSET if _type is None else _type
        type: Union[Unset, EvaluatorType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EvaluatorType(_type)

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            code_version_uid=code_version_uid,
            code_workflow_uid=code_workflow_uid,
            criteria_uid=criteria_uid,
            evaluator_uid=evaluator_uid,
            name=name,
            code_execution_uid=code_execution_uid,
            created_at=created_at,
            description=description,
            type=type,
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
