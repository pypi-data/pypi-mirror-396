from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="SamlResponseData")


@attrs.define
class SamlResponseData:
    """Includes metadata about the SAML response as well as access/refresh tokens for the Snorkel Flow UI.

    Attributes:
        access_token (str):
        refresh_token (str):
        redirect_to (Union[Unset, str]):
    """

    access_token: str
    refresh_token: str
    redirect_to: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        access_token = self.access_token
        refresh_token = self.refresh_token
        redirect_to = self.redirect_to

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        )
        if redirect_to is not UNSET:
            field_dict["redirect_to"] = redirect_to

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        access_token = d.pop("access_token")

        refresh_token = d.pop("refresh_token")

        _redirect_to = d.pop("redirect_to", UNSET)
        redirect_to = UNSET if _redirect_to is None else _redirect_to

        obj = cls(
            access_token=access_token,
            refresh_token=refresh_token,
            redirect_to=redirect_to,
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
