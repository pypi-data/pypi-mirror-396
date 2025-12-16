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
    from ..models.dataset_comment_response import DatasetCommentResponse  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DatasetCommentsByXuidResponse")


@attrs.define
class DatasetCommentsByXuidResponse:
    """
    Attributes:
        comments (List['DatasetCommentResponse']):
        x_uid (str):
    """

    comments: List["DatasetCommentResponse"]
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.dataset_comment_response import (
            DatasetCommentResponse,  # noqa: F401
        )
        # fmt: on
        comments = []
        for comments_item_data in self.comments:
            comments_item = comments_item_data.to_dict()
            comments.append(comments_item)

        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "comments": comments,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.dataset_comment_response import (
            DatasetCommentResponse,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        comments = []
        _comments = d.pop("comments")
        for comments_item_data in _comments:
            comments_item = DatasetCommentResponse.from_dict(comments_item_data)

            comments.append(comments_item)

        x_uid = d.pop("x_uid")

        obj = cls(
            comments=comments,
            x_uid=x_uid,
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
