from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteDatasourceResponse")


@attrs.define
class DeleteDatasourceResponse:
    """Response after deleting a datasource.

    Attributes:
        message (str):
        success (bool):
        datasource_uid (Union[Unset, int]):
        job_id (Union[Unset, str]):
    """

    message: str
    success: bool
    datasource_uid: Union[Unset, int] = UNSET
    job_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        message = self.message
        success = self.success
        datasource_uid = self.datasource_uid
        job_id = self.job_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "success": success,
            }
        )
        if datasource_uid is not UNSET:
            field_dict["datasource_uid"] = datasource_uid
        if job_id is not UNSET:
            field_dict["job_id"] = job_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message")

        success = d.pop("success")

        _datasource_uid = d.pop("datasource_uid", UNSET)
        datasource_uid = UNSET if _datasource_uid is None else _datasource_uid

        _job_id = d.pop("job_id", UNSET)
        job_id = UNSET if _job_id is None else _job_id

        obj = cls(
            message=message,
            success=success,
            datasource_uid=datasource_uid,
            job_id=job_id,
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
