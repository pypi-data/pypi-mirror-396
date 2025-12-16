from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.comment_tag_assets import CommentTagAssets  # noqa: F401
    from ..models.commit_gt_assets import CommitGTAssets  # noqa: F401
    from ..models.complete_batch_annotation_assets import (
        CompleteBatchAnnotationAssets,  # noqa: F401
    )
    from ..models.complete_long_running_lf_assets import (
        CompleteLongRunningLFAssets,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="NotificationBody")


@attrs.define
class NotificationBody:
    """
    Attributes:
        asset_uri (Union['CommentTagAssets', 'CommitGTAssets', 'CompleteBatchAnnotationAssets',
            'CompleteLongRunningLFAssets']):
        title (str):
        message (Union[Unset, str]):
    """

    asset_uri: Union[
        "CommentTagAssets",
        "CommitGTAssets",
        "CompleteBatchAnnotationAssets",
        "CompleteLongRunningLFAssets",
    ]
    title: str
    message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.comment_tag_assets import CommentTagAssets  # noqa: F401
        from ..models.commit_gt_assets import CommitGTAssets  # noqa: F401
        from ..models.complete_batch_annotation_assets import (
            CompleteBatchAnnotationAssets,  # noqa: F401
        )
        from ..models.complete_long_running_lf_assets import (
            CompleteLongRunningLFAssets,  # noqa: F401
        )
        # fmt: on
        asset_uri: Dict[str, Any]
        if isinstance(self.asset_uri, CommentTagAssets):
            asset_uri = self.asset_uri.to_dict()
        elif isinstance(self.asset_uri, CommitGTAssets):
            asset_uri = self.asset_uri.to_dict()
        elif isinstance(self.asset_uri, CompleteBatchAnnotationAssets):
            asset_uri = self.asset_uri.to_dict()
        else:
            asset_uri = self.asset_uri.to_dict()

        title = self.title
        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "asset_uri": asset_uri,
                "title": title,
            }
        )
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.comment_tag_assets import CommentTagAssets  # noqa: F401
        from ..models.commit_gt_assets import CommitGTAssets  # noqa: F401
        from ..models.complete_batch_annotation_assets import (
            CompleteBatchAnnotationAssets,  # noqa: F401
        )
        from ..models.complete_long_running_lf_assets import (
            CompleteLongRunningLFAssets,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()

        def _parse_asset_uri(
            data: object,
        ) -> Union[
            "CommentTagAssets",
            "CommitGTAssets",
            "CompleteBatchAnnotationAssets",
            "CompleteLongRunningLFAssets",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                asset_uri_type_0 = CommentTagAssets.from_dict(data)

                return asset_uri_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                asset_uri_type_1 = CommitGTAssets.from_dict(data)

                return asset_uri_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                asset_uri_type_2 = CompleteBatchAnnotationAssets.from_dict(data)

                return asset_uri_type_2
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            asset_uri_type_3 = CompleteLongRunningLFAssets.from_dict(data)

            return asset_uri_type_3

        asset_uri = _parse_asset_uri(d.pop("asset_uri"))

        title = d.pop("title")

        _message = d.pop("message", UNSET)
        message = UNSET if _message is None else _message

        obj = cls(
            asset_uri=asset_uri,
            title=title,
            message=message,
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
