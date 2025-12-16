from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="DeleteDatasetAnnotationsParams")


@attrs.define
class DeleteDatasetAnnotationsParams:
    """
    Attributes:
        annotation_uids (List[int]):
        dataset_uid (int):
        label_schema_uid (int):
    """

    annotation_uids: List[int]
    dataset_uid: int
    label_schema_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_uids = self.annotation_uids

        dataset_uid = self.dataset_uid
        label_schema_uid = self.label_schema_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uids": annotation_uids,
                "dataset_uid": dataset_uid,
                "label_schema_uid": label_schema_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_uids = cast(List[int], d.pop("annotation_uids"))

        dataset_uid = d.pop("dataset_uid")

        label_schema_uid = d.pop("label_schema_uid")

        obj = cls(
            annotation_uids=annotation_uids,
            dataset_uid=dataset_uid,
            label_schema_uid=label_schema_uid,
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
