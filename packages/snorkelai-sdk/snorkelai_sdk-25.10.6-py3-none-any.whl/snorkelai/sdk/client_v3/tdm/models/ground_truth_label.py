from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.supported_label_schema_type import SupportedLabelSchemaType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GroundTruthLabel")


@attrs.define
class GroundTruthLabel:
    """These are all fetched in real time from the label schema and ground truth tables

    Attributes:
        label_schema_name (str):
        label_schema_uid (int):
        label_description (Union[Unset, str]):
        label_name (Union[Unset, str]):
        label_ordinality (Union[Unset, int]):
        label_schema_description (Union[Unset, str]):
        label_schema_type (Union[Unset, SupportedLabelSchemaType]):
    """

    label_schema_name: str
    label_schema_uid: int
    label_description: Union[Unset, str] = UNSET
    label_name: Union[Unset, str] = UNSET
    label_ordinality: Union[Unset, int] = UNSET
    label_schema_description: Union[Unset, str] = UNSET
    label_schema_type: Union[Unset, SupportedLabelSchemaType] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        label_schema_name = self.label_schema_name
        label_schema_uid = self.label_schema_uid
        label_description = self.label_description
        label_name = self.label_name
        label_ordinality = self.label_ordinality
        label_schema_description = self.label_schema_description
        label_schema_type: Union[Unset, str] = UNSET
        if not isinstance(self.label_schema_type, Unset):
            label_schema_type = self.label_schema_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_schema_name": label_schema_name,
                "label_schema_uid": label_schema_uid,
            }
        )
        if label_description is not UNSET:
            field_dict["label_description"] = label_description
        if label_name is not UNSET:
            field_dict["label_name"] = label_name
        if label_ordinality is not UNSET:
            field_dict["label_ordinality"] = label_ordinality
        if label_schema_description is not UNSET:
            field_dict["label_schema_description"] = label_schema_description
        if label_schema_type is not UNSET:
            field_dict["label_schema_type"] = label_schema_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        label_schema_name = d.pop("label_schema_name")

        label_schema_uid = d.pop("label_schema_uid")

        _label_description = d.pop("label_description", UNSET)
        label_description = UNSET if _label_description is None else _label_description

        _label_name = d.pop("label_name", UNSET)
        label_name = UNSET if _label_name is None else _label_name

        _label_ordinality = d.pop("label_ordinality", UNSET)
        label_ordinality = UNSET if _label_ordinality is None else _label_ordinality

        _label_schema_description = d.pop("label_schema_description", UNSET)
        label_schema_description = (
            UNSET if _label_schema_description is None else _label_schema_description
        )

        _label_schema_type = d.pop("label_schema_type", UNSET)
        _label_schema_type = UNSET if _label_schema_type is None else _label_schema_type
        label_schema_type: Union[Unset, SupportedLabelSchemaType]
        if isinstance(_label_schema_type, Unset):
            label_schema_type = UNSET
        else:
            label_schema_type = SupportedLabelSchemaType(_label_schema_type)

        obj = cls(
            label_schema_name=label_schema_name,
            label_schema_uid=label_schema_uid,
            label_description=label_description,
            label_name=label_name,
            label_ordinality=label_ordinality,
            label_schema_description=label_schema_description,
            label_schema_type=label_schema_type,
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
