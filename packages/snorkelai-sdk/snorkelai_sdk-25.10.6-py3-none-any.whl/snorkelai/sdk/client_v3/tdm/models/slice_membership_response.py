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
    from ..models.slice_membership_response_additional_property import (
        SliceMembershipResponseAdditionalProperty,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SliceMembershipResponse")


@attrs.define
class SliceMembershipResponse:
    """Response is a direct mapping of x_uids to their slice membership info, maintaining the expected
    structure for frontend compatibility.

    """

    additional_properties: Dict[str, "SliceMembershipResponseAdditionalProperty"] = (
        attrs.field(init=False, factory=dict)
    )

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.slice_membership_response_additional_property import (
            SliceMembershipResponseAdditionalProperty,  # noqa: F401
        )
        # fmt: on

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.slice_membership_response_additional_property import (
            SliceMembershipResponseAdditionalProperty,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        obj = cls()
        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = SliceMembershipResponseAdditionalProperty.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        obj.additional_properties = additional_properties
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "SliceMembershipResponseAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: "SliceMembershipResponseAdditionalProperty"
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
