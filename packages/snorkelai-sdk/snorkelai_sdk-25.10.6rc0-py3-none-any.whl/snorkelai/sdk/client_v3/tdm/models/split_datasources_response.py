from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="SplitDatasourcesResponse")


@attrs.define
class SplitDatasourcesResponse:
    """Response for dataset splitting operations.

    Attributes:
        dataset_uid (int):
        job_uid (str):
    """

    dataset_uid: int
    job_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_uid = self.dataset_uid
        job_uid = self.job_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "job_uid": job_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        job_uid = d.pop("job_uid")

        obj = cls(
            dataset_uid=dataset_uid,
            job_uid=job_uid,
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
