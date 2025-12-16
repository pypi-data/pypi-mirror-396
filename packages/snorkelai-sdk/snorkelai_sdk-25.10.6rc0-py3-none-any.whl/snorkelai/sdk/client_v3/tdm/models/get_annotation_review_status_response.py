from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_review_data import AnnotationReviewData  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetAnnotationReviewStatusResponse")


@attrs.define
class GetAnnotationReviewStatusResponse:
    """
    Attributes:
        review_status (List['AnnotationReviewData']):
    """

    review_status: List["AnnotationReviewData"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_review_data import AnnotationReviewData  # noqa: F401
        # fmt: on
        review_status = []
        for review_status_item_data in self.review_status:
            review_status_item = review_status_item_data.to_dict()
            review_status.append(review_status_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "review_status": review_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_review_data import AnnotationReviewData  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        review_status = []
        _review_status = d.pop("review_status")
        for review_status_item_data in _review_status:
            review_status_item = AnnotationReviewData.from_dict(review_status_item_data)

            review_status.append(review_status_item)

        obj = cls(
            review_status=review_status,
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
