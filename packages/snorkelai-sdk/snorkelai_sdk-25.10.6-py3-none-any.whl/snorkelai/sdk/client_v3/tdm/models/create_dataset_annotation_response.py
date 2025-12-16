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
    from ..models.svc_source import SvcSource  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreateDatasetAnnotationResponse")


@attrs.define
class CreateDatasetAnnotationResponse:
    """
    Attributes:
        annotation_uid (int):
        source (Union[Unset, SvcSource]):
    """

    annotation_uid: int
    source: Union[Unset, "SvcSource"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        annotation_uid = self.annotation_uid
        source: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.svc_source import SvcSource  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        _source = d.pop("source", UNSET)
        _source = UNSET if _source is None else _source
        source: Union[Unset, SvcSource]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = SvcSource.from_dict(_source)

        obj = cls(
            annotation_uid=annotation_uid,
            source=source,
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
