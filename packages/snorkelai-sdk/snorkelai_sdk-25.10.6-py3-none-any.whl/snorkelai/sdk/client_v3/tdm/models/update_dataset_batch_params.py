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

T = TypeVar("T", bound="UpdateDatasetBatchParams")


@attrs.define
class UpdateDatasetBatchParams:
    """
    Attributes:
        assignees (Union[Unset, List[int]]):
        batch_name (Union[Unset, str]):
        expert_source_uid (Union[Unset, int]):
        unassign_expert_source_uid (Union[Unset, int]):
    """

    assignees: Union[Unset, List[int]] = UNSET
    batch_name: Union[Unset, str] = UNSET
    expert_source_uid: Union[Unset, int] = UNSET
    unassign_expert_source_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        assignees: Union[Unset, List[int]] = UNSET
        if not isinstance(self.assignees, Unset):
            assignees = self.assignees

        batch_name = self.batch_name
        expert_source_uid = self.expert_source_uid
        unassign_expert_source_uid = self.unassign_expert_source_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if batch_name is not UNSET:
            field_dict["batch_name"] = batch_name
        if expert_source_uid is not UNSET:
            field_dict["expert_source_uid"] = expert_source_uid
        if unassign_expert_source_uid is not UNSET:
            field_dict["unassign_expert_source_uid"] = unassign_expert_source_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _assignees = d.pop("assignees", UNSET)
        assignees = cast(List[int], UNSET if _assignees is None else _assignees)

        _batch_name = d.pop("batch_name", UNSET)
        batch_name = UNSET if _batch_name is None else _batch_name

        _expert_source_uid = d.pop("expert_source_uid", UNSET)
        expert_source_uid = UNSET if _expert_source_uid is None else _expert_source_uid

        _unassign_expert_source_uid = d.pop("unassign_expert_source_uid", UNSET)
        unassign_expert_source_uid = (
            UNSET
            if _unassign_expert_source_uid is None
            else _unassign_expert_source_uid
        )

        obj = cls(
            assignees=assignees,
            batch_name=batch_name,
            expert_source_uid=expert_source_uid,
            unassign_expert_source_uid=unassign_expert_source_uid,
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
