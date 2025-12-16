from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.annotation_review_state import AnnotationReviewState

T = TypeVar("T", bound="UpdateAnnotationReviewStatusParamsItemReviewStatus")


@attrs.define
class UpdateAnnotationReviewStatusParamsItemReviewStatus:
    """ """

    additional_properties: Dict[str, AnnotationReviewState] = attrs.field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.value
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        obj = cls()
        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = AnnotationReviewState(prop_dict)

            additional_properties[prop_name] = additional_property

        obj.additional_properties = additional_properties
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> AnnotationReviewState:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: AnnotationReviewState) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
