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

from ..models.criteria_state import CriteriaState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.output_format import OutputFormat  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Criteria")


@attrs.define
class Criteria:
    """
    Attributes:
        benchmark_uid (int):
        criteria_uid (int):
        dataset_uid (int):
        name (str):
        output_format (OutputFormat):
        state (CriteriaState):
        created_at (Union[Unset, datetime.datetime]):
        description (Union[Unset, str]):
        filter_config (Union[Unset, str]):
        is_default (Union[Unset, bool]):  Default: False.
        updated_at (Union[Unset, datetime.datetime]):
        user_id (Union[Unset, int]):
    """

    benchmark_uid: int
    criteria_uid: int
    dataset_uid: int
    name: str
    output_format: "OutputFormat"
    state: CriteriaState
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    filter_config: Union[Unset, str] = UNSET
    is_default: Union[Unset, bool] = False
    updated_at: Union[Unset, datetime.datetime] = UNSET
    user_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.output_format import OutputFormat  # noqa: F401
        # fmt: on
        benchmark_uid = self.benchmark_uid
        criteria_uid = self.criteria_uid
        dataset_uid = self.dataset_uid
        name = self.name
        output_format = self.output_format.to_dict()
        state = self.state.value
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description
        filter_config = self.filter_config
        is_default = self.is_default
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()
        user_id = self.user_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_uid": benchmark_uid,
                "criteria_uid": criteria_uid,
                "dataset_uid": dataset_uid,
                "name": name,
                "output_format": output_format,
                "state": state,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if filter_config is not UNSET:
            field_dict["filter_config"] = filter_config
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.output_format import OutputFormat  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        benchmark_uid = d.pop("benchmark_uid")

        criteria_uid = d.pop("criteria_uid")

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        output_format = OutputFormat.from_dict(d.pop("output_format"))

        state = CriteriaState(d.pop("state"))

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _filter_config = d.pop("filter_config", UNSET)
        filter_config = UNSET if _filter_config is None else _filter_config

        _is_default = d.pop("is_default", UNSET)
        is_default = UNSET if _is_default is None else _is_default

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _user_id = d.pop("user_id", UNSET)
        user_id = UNSET if _user_id is None else _user_id

        obj = cls(
            benchmark_uid=benchmark_uid,
            criteria_uid=criteria_uid,
            dataset_uid=dataset_uid,
            name=name,
            output_format=output_format,
            state=state,
            created_at=created_at,
            description=description,
            filter_config=filter_config,
            is_default=is_default,
            updated_at=updated_at,
            user_id=user_id,
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
