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

T = TypeVar("T", bound="CreateBenchmarkExecutionPayload")


@attrs.define
class CreateBenchmarkExecutionPayload:
    """
    Attributes:
        dataset_uid (int):
        criteria_uids (Union[Unset, List[int]]):
        datasource_uids (Union[Unset, List[int]]):
        description (Union[Unset, str]):
        name (Union[Unset, str]):
        splits (Union[Unset, List[str]]):
    """

    dataset_uid: int
    criteria_uids: Union[Unset, List[int]] = UNSET
    datasource_uids: Union[Unset, List[int]] = UNSET
    description: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    splits: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_uid = self.dataset_uid
        criteria_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.criteria_uids, Unset):
            criteria_uids = self.criteria_uids

        datasource_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.datasource_uids, Unset):
            datasource_uids = self.datasource_uids

        description = self.description
        name = self.name
        splits: Union[Unset, List[str]] = UNSET
        if not isinstance(self.splits, Unset):
            splits = self.splits

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
            }
        )
        if criteria_uids is not UNSET:
            field_dict["criteria_uids"] = criteria_uids
        if datasource_uids is not UNSET:
            field_dict["datasource_uids"] = datasource_uids
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if splits is not UNSET:
            field_dict["splits"] = splits

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        _criteria_uids = d.pop("criteria_uids", UNSET)
        criteria_uids = cast(
            List[int], UNSET if _criteria_uids is None else _criteria_uids
        )

        _datasource_uids = d.pop("datasource_uids", UNSET)
        datasource_uids = cast(
            List[int], UNSET if _datasource_uids is None else _datasource_uids
        )

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _name = d.pop("name", UNSET)
        name = UNSET if _name is None else _name

        _splits = d.pop("splits", UNSET)
        splits = cast(List[str], UNSET if _splits is None else _splits)

        obj = cls(
            dataset_uid=dataset_uid,
            criteria_uids=criteria_uids,
            datasource_uids=datasource_uids,
            description=description,
            name=name,
            splits=splits,
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
