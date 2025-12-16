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

from ..models.workflow_state import WorkflowState
from ..models.workflow_type import WorkflowType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetWorkflowResponse")


@attrs.define
class GetWorkflowResponse:
    """
    Attributes:
        created_by_user_uid (int):
        name (str):
        type (WorkflowType):
        workflow_uid (int):
        workspace_uid (int):
        created_at (Union[Unset, datetime.datetime]):
        created_by_username (Union[Unset, str]):
        input_dataset_uid (Union[Unset, int]):
        output_dataset_uid (Union[Unset, int]):
        state (Union[Unset, WorkflowState]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    created_by_user_uid: int
    name: str
    type: WorkflowType
    workflow_uid: int
    workspace_uid: int
    created_at: Union[Unset, datetime.datetime] = UNSET
    created_by_username: Union[Unset, str] = UNSET
    input_dataset_uid: Union[Unset, int] = UNSET
    output_dataset_uid: Union[Unset, int] = UNSET
    state: Union[Unset, WorkflowState] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_by_user_uid = self.created_by_user_uid
        name = self.name
        type = self.type.value
        workflow_uid = self.workflow_uid
        workspace_uid = self.workspace_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        created_by_username = self.created_by_username
        input_dataset_uid = self.input_dataset_uid
        output_dataset_uid = self.output_dataset_uid
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_by_user_uid": created_by_user_uid,
                "name": name,
                "type": type,
                "workflow_uid": workflow_uid,
                "workspace_uid": workspace_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by_username is not UNSET:
            field_dict["created_by_username"] = created_by_username
        if input_dataset_uid is not UNSET:
            field_dict["input_dataset_uid"] = input_dataset_uid
        if output_dataset_uid is not UNSET:
            field_dict["output_dataset_uid"] = output_dataset_uid
        if state is not UNSET:
            field_dict["state"] = state
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_by_user_uid = d.pop("created_by_user_uid")

        name = d.pop("name")

        type = WorkflowType(d.pop("type"))

        workflow_uid = d.pop("workflow_uid")

        workspace_uid = d.pop("workspace_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _created_by_username = d.pop("created_by_username", UNSET)
        created_by_username = (
            UNSET if _created_by_username is None else _created_by_username
        )

        _input_dataset_uid = d.pop("input_dataset_uid", UNSET)
        input_dataset_uid = UNSET if _input_dataset_uid is None else _input_dataset_uid

        _output_dataset_uid = d.pop("output_dataset_uid", UNSET)
        output_dataset_uid = (
            UNSET if _output_dataset_uid is None else _output_dataset_uid
        )

        _state = d.pop("state", UNSET)
        _state = UNSET if _state is None else _state
        state: Union[Unset, WorkflowState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = WorkflowState(_state)

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            created_by_user_uid=created_by_user_uid,
            name=name,
            type=type,
            workflow_uid=workflow_uid,
            workspace_uid=workspace_uid,
            created_at=created_at,
            created_by_username=created_by_username,
            input_dataset_uid=input_dataset_uid,
            output_dataset_uid=output_dataset_uid,
            state=state,
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
