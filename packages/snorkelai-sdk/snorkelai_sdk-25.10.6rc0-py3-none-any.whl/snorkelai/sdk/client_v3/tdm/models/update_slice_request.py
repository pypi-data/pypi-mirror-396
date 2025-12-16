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
    from ..models.slice_creation_request import SliceCreationRequest  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="UpdateSliceRequest")


@attrs.define
class UpdateSliceRequest:
    """
    Attributes:
        slice_ (SliceCreationRequest):
    """

    slice_: "SliceCreationRequest"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.slice_creation_request import SliceCreationRequest  # noqa: F401
        # fmt: on
        slice_ = self.slice_.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slice": slice_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.slice_creation_request import SliceCreationRequest  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        slice_ = SliceCreationRequest.from_dict(d.pop("slice"))

        obj = cls(
            slice_=slice_,
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
