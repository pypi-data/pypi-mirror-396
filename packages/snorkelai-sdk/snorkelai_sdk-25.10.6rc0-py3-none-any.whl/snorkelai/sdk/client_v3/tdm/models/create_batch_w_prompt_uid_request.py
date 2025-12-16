from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateBatchWPromptUidRequest")


@attrs.define
class CreateBatchWPromptUidRequest:
    """
    Attributes:
        assignees (List[int]):
        batch_name (str):
        label_schema_uids (List[int]):
        workflow_uid (int):
        prompt_execution_uids (Union[Unset, List[int]]):
        prompt_uid (Union[Unset, int]):
    """

    assignees: List[int]
    batch_name: str
    label_schema_uids: List[int]
    workflow_uid: int
    prompt_execution_uids: Union[Unset, List[int]] = UNSET
    prompt_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        assignees = self.assignees

        batch_name = self.batch_name
        label_schema_uids = self.label_schema_uids

        workflow_uid = self.workflow_uid
        prompt_execution_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.prompt_execution_uids, Unset):
            prompt_execution_uids = self.prompt_execution_uids

        prompt_uid = self.prompt_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assignees": assignees,
                "batch_name": batch_name,
                "label_schema_uids": label_schema_uids,
                "workflow_uid": workflow_uid,
            }
        )
        if prompt_execution_uids is not UNSET:
            field_dict["prompt_execution_uids"] = prompt_execution_uids
        if prompt_uid is not UNSET:
            field_dict["prompt_uid"] = prompt_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assignees = cast(List[int], d.pop("assignees"))

        batch_name = d.pop("batch_name")

        label_schema_uids = cast(List[int], d.pop("label_schema_uids"))

        workflow_uid = d.pop("workflow_uid")

        _prompt_execution_uids = d.pop("prompt_execution_uids", UNSET)
        prompt_execution_uids = cast(
            List[int],
            UNSET if _prompt_execution_uids is None else _prompt_execution_uids,
        )

        _prompt_uid = d.pop("prompt_uid", UNSET)
        prompt_uid = UNSET if _prompt_uid is None else _prompt_uid

        obj = cls(
            assignees=assignees,
            batch_name=batch_name,
            label_schema_uids=label_schema_uids,
            workflow_uid=workflow_uid,
            prompt_execution_uids=prompt_execution_uids,
            prompt_uid=prompt_uid,
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
