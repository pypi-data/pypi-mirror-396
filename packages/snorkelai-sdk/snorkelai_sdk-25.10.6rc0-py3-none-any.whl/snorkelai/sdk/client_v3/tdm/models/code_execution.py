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

T = TypeVar("T", bound="CodeExecution")


@attrs.define
class CodeExecution:
    """
    Attributes:
        code_execution_uid (int):
        code_version_uid (int):
        created_by_user_uid (int):
        vds_uid (int):
        created_at (Union[Unset, datetime.datetime]):
        job_uid (Union[Unset, str]):
        updated_at (Union[Unset, datetime.datetime]):
    """

    code_execution_uid: int
    code_version_uid: int
    created_by_user_uid: int
    vds_uid: int
    created_at: Union[Unset, datetime.datetime] = UNSET
    job_uid: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        code_execution_uid = self.code_execution_uid
        code_version_uid = self.code_version_uid
        created_by_user_uid = self.created_by_user_uid
        vds_uid = self.vds_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        job_uid = self.job_uid
        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code_execution_uid": code_execution_uid,
                "code_version_uid": code_version_uid,
                "created_by_user_uid": created_by_user_uid,
                "vds_uid": vds_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if job_uid is not UNSET:
            field_dict["job_uid"] = job_uid
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        code_execution_uid = d.pop("code_execution_uid")

        code_version_uid = d.pop("code_version_uid")

        created_by_user_uid = d.pop("created_by_user_uid")

        vds_uid = d.pop("vds_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _job_uid = d.pop("job_uid", UNSET)
        job_uid = UNSET if _job_uid is None else _job_uid

        _updated_at = d.pop("updated_at", UNSET)
        _updated_at = UNSET if _updated_at is None else _updated_at
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        obj = cls(
            code_execution_uid=code_execution_uid,
            code_version_uid=code_version_uid,
            created_by_user_uid=created_by_user_uid,
            vds_uid=vds_uid,
            created_at=created_at,
            job_uid=job_uid,
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
