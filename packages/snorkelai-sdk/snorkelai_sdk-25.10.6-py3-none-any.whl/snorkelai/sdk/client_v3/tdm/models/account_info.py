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

from ..types import UNSET, Unset

T = TypeVar("T", bound="AccountInfo")


@attrs.define
class AccountInfo:
    """
    Attributes:
        account_id (str):
        dataset_limit (int):
        expiration_date (datetime.datetime):
        seat_limit (int):
        application_limit (Union[Unset, int]):
        system_validation_key (Union[Unset, str]):
        trial (Union[Unset, int]):
        validate_system (Union[Unset, bool]):  Default: True.
    """

    account_id: str
    dataset_limit: int
    expiration_date: datetime.datetime
    seat_limit: int
    application_limit: Union[Unset, int] = UNSET
    system_validation_key: Union[Unset, str] = UNSET
    trial: Union[Unset, int] = UNSET
    validate_system: Union[Unset, bool] = True
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        account_id = self.account_id
        dataset_limit = self.dataset_limit
        expiration_date = self.expiration_date.isoformat()
        seat_limit = self.seat_limit
        application_limit = self.application_limit
        system_validation_key = self.system_validation_key
        trial = self.trial
        validate_system = self.validate_system

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account_id": account_id,
                "dataset_limit": dataset_limit,
                "expiration_date": expiration_date,
                "seat_limit": seat_limit,
            }
        )
        if application_limit is not UNSET:
            field_dict["application_limit"] = application_limit
        if system_validation_key is not UNSET:
            field_dict["system_validation_key"] = system_validation_key
        if trial is not UNSET:
            field_dict["trial"] = trial
        if validate_system is not UNSET:
            field_dict["validate_system"] = validate_system

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        account_id = d.pop("account_id")

        dataset_limit = d.pop("dataset_limit")

        expiration_date = isoparse(d.pop("expiration_date"))

        seat_limit = d.pop("seat_limit")

        _application_limit = d.pop("application_limit", UNSET)
        application_limit = UNSET if _application_limit is None else _application_limit

        _system_validation_key = d.pop("system_validation_key", UNSET)
        system_validation_key = (
            UNSET if _system_validation_key is None else _system_validation_key
        )

        _trial = d.pop("trial", UNSET)
        trial = UNSET if _trial is None else _trial

        _validate_system = d.pop("validate_system", UNSET)
        validate_system = UNSET if _validate_system is None else _validate_system

        obj = cls(
            account_id=account_id,
            dataset_limit=dataset_limit,
            expiration_date=expiration_date,
            seat_limit=seat_limit,
            application_limit=application_limit,
            system_validation_key=system_validation_key,
            trial=trial,
            validate_system=validate_system,
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
