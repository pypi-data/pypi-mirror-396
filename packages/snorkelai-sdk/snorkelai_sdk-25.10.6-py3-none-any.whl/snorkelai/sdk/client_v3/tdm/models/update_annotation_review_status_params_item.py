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
    from ..models.update_annotation_review_status_params_item_review_status import (
        UpdateAnnotationReviewStatusParamsItemReviewStatus,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdateAnnotationReviewStatusParamsItem")


@attrs.define
class UpdateAnnotationReviewStatusParamsItem:
    """
    Attributes:
        annotation_uid (int):
        review_status (UpdateAnnotationReviewStatusParamsItemReviewStatus):
    """

    annotation_uid: int
    review_status: "UpdateAnnotationReviewStatusParamsItemReviewStatus"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_annotation_review_status_params_item_review_status import (
            UpdateAnnotationReviewStatusParamsItemReviewStatus,  # noqa: F401
        )
        # fmt: on
        annotation_uid = self.annotation_uid
        review_status = self.review_status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
                "review_status": review_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_annotation_review_status_params_item_review_status import (
            UpdateAnnotationReviewStatusParamsItemReviewStatus,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        review_status = UpdateAnnotationReviewStatusParamsItemReviewStatus.from_dict(
            d.pop("review_status")
        )

        obj = cls(
            annotation_uid=annotation_uid,
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
