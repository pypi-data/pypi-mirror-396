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

T = TypeVar("T", bound="GarbageCollectDatasetApplicationParams")


@attrs.define
class GarbageCollectDatasetApplicationParams:
    """
    Attributes:
        application_uid (Union[Unset, int]):
        dataset_uid (Union[Unset, int]):
        repeat_period (Union[Unset, str]):
        workspace_uids (Union[Unset, List[int]]):
    """

    application_uid: Union[Unset, int] = UNSET
    dataset_uid: Union[Unset, int] = UNSET
    repeat_period: Union[Unset, str] = UNSET
    workspace_uids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        application_uid = self.application_uid
        dataset_uid = self.dataset_uid
        repeat_period = self.repeat_period
        workspace_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.workspace_uids, Unset):
            workspace_uids = self.workspace_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if application_uid is not UNSET:
            field_dict["application_uid"] = application_uid
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if repeat_period is not UNSET:
            field_dict["repeat_period"] = repeat_period
        if workspace_uids is not UNSET:
            field_dict["workspace_uids"] = workspace_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _application_uid = d.pop("application_uid", UNSET)
        application_uid = UNSET if _application_uid is None else _application_uid

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _repeat_period = d.pop("repeat_period", UNSET)
        repeat_period = UNSET if _repeat_period is None else _repeat_period

        _workspace_uids = d.pop("workspace_uids", UNSET)
        workspace_uids = cast(
            List[int], UNSET if _workspace_uids is None else _workspace_uids
        )

        obj = cls(
            application_uid=application_uid,
            dataset_uid=dataset_uid,
            repeat_period=repeat_period,
            workspace_uids=workspace_uids,
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
