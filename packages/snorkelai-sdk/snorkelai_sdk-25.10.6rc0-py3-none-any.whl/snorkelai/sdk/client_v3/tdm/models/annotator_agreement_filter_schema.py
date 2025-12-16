from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotatorAgreementFilterSchema")


@attrs.define
class AnnotatorAgreementFilterSchema:
    """
    Attributes:
        annotator_uid_one (int):
        annotator_uid_two (int):
        label_schema_uid (int):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        transform_config_type (Union[Literal['annotator_agreement_filter_schema'], Unset]):  Default:
            'annotator_agreement_filter_schema'.
        vote_type (Union[Unset, str]):
        voted (Union[Unset, str]):  Default: ''.
    """

    annotator_uid_one: int
    annotator_uid_two: int
    label_schema_uid: int
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    transform_config_type: Union[
        Literal["annotator_agreement_filter_schema"], Unset
    ] = "annotator_agreement_filter_schema"
    vote_type: Union[Unset, str] = UNSET
    voted: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotator_uid_one = self.annotator_uid_one
        annotator_uid_two = self.annotator_uid_two
        label_schema_uid = self.label_schema_uid
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        transform_config_type = self.transform_config_type
        vote_type = self.vote_type
        voted = self.voted

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotator_uid_one": annotator_uid_one,
                "annotator_uid_two": annotator_uid_two,
                "label_schema_uid": label_schema_uid,
            }
        )
        if filter_type is not UNSET:
            field_dict["filter_type"] = filter_type
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type
        if vote_type is not UNSET:
            field_dict["vote_type"] = vote_type
        if voted is not UNSET:
            field_dict["voted"] = voted

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotator_uid_one = d.pop("annotator_uid_one")

        annotator_uid_two = d.pop("annotator_uid_two")

        label_schema_uid = d.pop("label_schema_uid")

        _filter_type = d.pop("filter_type", UNSET)
        _filter_type = UNSET if _filter_type is None else _filter_type
        filter_type: Union[Unset, FilterTransformFilterTypes]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = FilterTransformFilterTypes(_filter_type)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        _vote_type = d.pop("vote_type", UNSET)
        vote_type = UNSET if _vote_type is None else _vote_type

        _voted = d.pop("voted", UNSET)
        voted = UNSET if _voted is None else _voted

        obj = cls(
            annotator_uid_one=annotator_uid_one,
            annotator_uid_two=annotator_uid_two,
            label_schema_uid=label_schema_uid,
            filter_type=filter_type,
            transform_config_type=transform_config_type,
            vote_type=vote_type,
            voted=voted,
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
