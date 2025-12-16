from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="AssignLabelSchemasToBatchParams")


@attrs.define
class AssignLabelSchemasToBatchParams:
    """
    Attributes:
        dataset_batch_uid (int):
        label_schema_uids (List[int]):
    """

    dataset_batch_uid: int
    label_schema_uids: List[int]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        dataset_batch_uid = self.dataset_batch_uid
        label_schema_uids = self.label_schema_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_batch_uid": dataset_batch_uid,
                "label_schema_uids": label_schema_uids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dataset_batch_uid = d.pop("dataset_batch_uid")

        label_schema_uids = cast(List[int], d.pop("label_schema_uids"))

        obj = cls(
            dataset_batch_uid=dataset_batch_uid,
            label_schema_uids=label_schema_uids,
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
