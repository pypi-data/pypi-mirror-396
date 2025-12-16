from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.workflow_type import WorkflowType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateWorkflowPayload")


@attrs.define
class CreateWorkflowPayload:
    """
    Attributes:
        name (str):
        type (WorkflowType):
        workspace_uid (int):
        input_dataset_uid (Union[Unset, int]):
    """

    name: str
    type: WorkflowType
    workspace_uid: int
    input_dataset_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type = self.type.value
        workspace_uid = self.workspace_uid
        input_dataset_uid = self.input_dataset_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type,
                "workspace_uid": workspace_uid,
            }
        )
        if input_dataset_uid is not UNSET:
            field_dict["input_dataset_uid"] = input_dataset_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type = WorkflowType(d.pop("type"))

        workspace_uid = d.pop("workspace_uid")

        _input_dataset_uid = d.pop("input_dataset_uid", UNSET)
        input_dataset_uid = UNSET if _input_dataset_uid is None else _input_dataset_uid

        obj = cls(
            name=name,
            type=type,
            workspace_uid=workspace_uid,
            input_dataset_uid=input_dataset_uid,
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
