import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="APIKey")


@attrs.define
class APIKey:
    """Used for the creation, validation, and deletion of user API keys

    Implementation Note - API Keys do not have quite the same level of security as
    user passwords (which use rotating salts and updated hashes) because API keys are
    long random strings to begin with. There is no such thing as a lookup table
    attack against API keys. We simply hash them using the safe sha256 and only store
    the hash, which would prevent a leaked table from granting unauth'd access
    (since the attacker would only have the hashes).

        Attributes:
            user_uid (int):
            api_key_peek (Union[Unset, str]):
            api_key_plaintext (Union[Unset, str]):
            api_key_uid (Union[Unset, int]):
            created_at (Union[Unset, datetime.datetime]):
            description (Union[Unset, str]):
    """

    user_uid: int
    api_key_peek: Union[Unset, str] = UNSET
    api_key_plaintext: Union[Unset, str] = UNSET
    api_key_uid: Union[Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_uid = self.user_uid
        api_key_peek = self.api_key_peek
        api_key_plaintext = self.api_key_plaintext
        api_key_uid = self.api_key_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_uid": user_uid,
            }
        )
        if api_key_peek is not UNSET:
            field_dict["api_key_peek"] = api_key_peek
        if api_key_plaintext is not UNSET:
            field_dict["api_key_plaintext"] = api_key_plaintext
        if api_key_uid is not UNSET:
            field_dict["api_key_uid"] = api_key_uid
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_uid = d.pop("user_uid")

        _api_key_peek = d.pop("api_key_peek", UNSET)
        api_key_peek = UNSET if _api_key_peek is None else _api_key_peek

        _api_key_plaintext = d.pop("api_key_plaintext", UNSET)
        api_key_plaintext = UNSET if _api_key_plaintext is None else _api_key_plaintext

        _api_key_uid = d.pop("api_key_uid", UNSET)
        api_key_uid = UNSET if _api_key_uid is None else _api_key_uid

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        obj = cls(
            user_uid=user_uid,
            api_key_peek=api_key_peek,
            api_key_plaintext=api_key_plaintext,
            api_key_uid=api_key_uid,
            created_at=created_at,
            description=description,
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
