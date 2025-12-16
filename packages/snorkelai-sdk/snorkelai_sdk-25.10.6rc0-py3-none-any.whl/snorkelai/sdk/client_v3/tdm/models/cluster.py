import datetime
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
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Cluster")


@attrs.define
class Cluster:
    """Model for error clusters that group similar failure patterns.

    Attributes:
        cluster_uid (int):
        created_at (datetime.datetime):
        error_analysis_uid (int):
        name (str):
        updated_at (datetime.datetime):
        datapoint_count (Union[Unset, int]):  Default: 0.
        description (Union[Unset, str]):
        examples (Union[Unset, List[str]]):
        improvement_strategy (Union[Unset, str]):
        virtualized_dataset_uid (Union[Unset, int]):
    """

    cluster_uid: int
    created_at: datetime.datetime
    error_analysis_uid: int
    name: str
    updated_at: datetime.datetime
    datapoint_count: Union[Unset, int] = 0
    description: Union[Unset, str] = UNSET
    examples: Union[Unset, List[str]] = UNSET
    improvement_strategy: Union[Unset, str] = UNSET
    virtualized_dataset_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cluster_uid = self.cluster_uid
        created_at = self.created_at.isoformat()
        error_analysis_uid = self.error_analysis_uid
        name = self.name
        updated_at = self.updated_at.isoformat()
        datapoint_count = self.datapoint_count
        description = self.description
        examples: Union[Unset, List[str]] = UNSET
        if not isinstance(self.examples, Unset):
            examples = self.examples

        improvement_strategy = self.improvement_strategy
        virtualized_dataset_uid = self.virtualized_dataset_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cluster_uid": cluster_uid,
                "created_at": created_at,
                "error_analysis_uid": error_analysis_uid,
                "name": name,
                "updated_at": updated_at,
            }
        )
        if datapoint_count is not UNSET:
            field_dict["datapoint_count"] = datapoint_count
        if description is not UNSET:
            field_dict["description"] = description
        if examples is not UNSET:
            field_dict["examples"] = examples
        if improvement_strategy is not UNSET:
            field_dict["improvement_strategy"] = improvement_strategy
        if virtualized_dataset_uid is not UNSET:
            field_dict["virtualized_dataset_uid"] = virtualized_dataset_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cluster_uid = d.pop("cluster_uid")

        created_at = isoparse(d.pop("created_at"))

        error_analysis_uid = d.pop("error_analysis_uid")

        name = d.pop("name")

        updated_at = isoparse(d.pop("updated_at"))

        _datapoint_count = d.pop("datapoint_count", UNSET)
        datapoint_count = UNSET if _datapoint_count is None else _datapoint_count

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _examples = d.pop("examples", UNSET)
        examples = cast(List[str], UNSET if _examples is None else _examples)

        _improvement_strategy = d.pop("improvement_strategy", UNSET)
        improvement_strategy = (
            UNSET if _improvement_strategy is None else _improvement_strategy
        )

        _virtualized_dataset_uid = d.pop("virtualized_dataset_uid", UNSET)
        virtualized_dataset_uid = (
            UNSET if _virtualized_dataset_uid is None else _virtualized_dataset_uid
        )

        obj = cls(
            cluster_uid=cluster_uid,
            created_at=created_at,
            error_analysis_uid=error_analysis_uid,
            name=name,
            updated_at=updated_at,
            datapoint_count=datapoint_count,
            description=description,
            examples=examples,
            improvement_strategy=improvement_strategy,
            virtualized_dataset_uid=virtualized_dataset_uid,
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
