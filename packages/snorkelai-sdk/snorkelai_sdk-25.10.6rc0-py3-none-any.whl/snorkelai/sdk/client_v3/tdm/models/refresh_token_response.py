from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="RefreshTokenResponse")


@attrs.define
class RefreshTokenResponse:
    """
    Attributes:
        access_token (str):
        expires_in (str):
        refresh_token (str):
        token_type (str):
    """

    access_token: str
    expires_in: str
    refresh_token: str
    token_type: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        access_token = self.access_token
        expires_in = self.expires_in
        refresh_token = self.refresh_token
        token_type = self.token_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "expires_in": expires_in,
                "refresh_token": refresh_token,
                "token_type": token_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        access_token = d.pop("access_token")

        expires_in = d.pop("expires_in")

        refresh_token = d.pop("refresh_token")

        token_type = d.pop("token_type")

        obj = cls(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
            token_type=token_type,
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
