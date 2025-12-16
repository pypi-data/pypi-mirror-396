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
    from ..models.update_annotation_review_status_params_item import (
        UpdateAnnotationReviewStatusParamsItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdateAnnotationReviewStatusParams")


@attrs.define
class UpdateAnnotationReviewStatusParams:
    """
    Attributes:
        dataset_uid (int):
        review_status_updates (List['UpdateAnnotationReviewStatusParamsItem']):
    """

    dataset_uid: int
    review_status_updates: List["UpdateAnnotationReviewStatusParamsItem"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_annotation_review_status_params_item import (
            UpdateAnnotationReviewStatusParamsItem,  # noqa: F401
        )
        # fmt: on
        dataset_uid = self.dataset_uid
        review_status_updates = []
        for review_status_updates_item_data in self.review_status_updates:
            review_status_updates_item = review_status_updates_item_data.to_dict()
            review_status_updates.append(review_status_updates_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "review_status_updates": review_status_updates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_annotation_review_status_params_item import (
            UpdateAnnotationReviewStatusParamsItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        review_status_updates = []
        _review_status_updates = d.pop("review_status_updates")
        for review_status_updates_item_data in _review_status_updates:
            review_status_updates_item = (
                UpdateAnnotationReviewStatusParamsItem.from_dict(
                    review_status_updates_item_data
                )
            )

            review_status_updates.append(review_status_updates_item)

        obj = cls(
            dataset_uid=dataset_uid,
            review_status_updates=review_status_updates,
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
