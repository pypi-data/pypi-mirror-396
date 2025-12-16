from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="DatasetBatchMetadata")


@attrs.define
class DatasetBatchMetadata:
    """
    Attributes:
        annotation_uid (int):
        batch_uids (List[int]):
        names (List[str]):
    """

    annotation_uid: int
    batch_uids: List[int]
    names: List[str]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_uid = self.annotation_uid
        batch_uids = self.batch_uids

        names = self.names

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
                "batch_uids": batch_uids,
                "names": names,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        batch_uids = cast(List[int], d.pop("batch_uids"))

        names = cast(List[str], d.pop("names"))

        obj = cls(
            annotation_uid=annotation_uid,
            batch_uids=batch_uids,
            names=names,
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
