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
    from ..models.invite_response import InviteResponse  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetInvitesResponse")


@attrs.define
class GetInvitesResponse:
    """
    Attributes:
        invites (List['InviteResponse']):
    """

    invites: List["InviteResponse"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.invite_response import InviteResponse  # noqa: F401
        # fmt: on
        invites = []
        for invites_item_data in self.invites:
            invites_item = invites_item_data.to_dict()
            invites.append(invites_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "invites": invites,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.invite_response import InviteResponse  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        invites = []
        _invites = d.pop("invites")
        for invites_item_data in _invites:
            invites_item = InviteResponse.from_dict(invites_item_data)

            invites.append(invites_item)

        obj = cls(
            invites=invites,
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
