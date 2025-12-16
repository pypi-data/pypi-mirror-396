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

T = TypeVar("T", bound="APIKeyLimited")


@attrs.define
class APIKeyLimited:
    """Structure of the API key that is returned when listing API keys for an existing user,
    note that this does not include the plaintext as by this time the plaintext has been thrown away

        Attributes:
            api_key_peek (str):
            api_key_uid (int):
            created_at (datetime.datetime):
            user_uid (int):
            description (Union[Unset, str]):
    """

    api_key_peek: str
    api_key_uid: int
    created_at: datetime.datetime
    user_uid: int
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_key_peek = self.api_key_peek
        api_key_uid = self.api_key_uid
        created_at = self.created_at.isoformat()
        user_uid = self.user_uid
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api_key_peek": api_key_peek,
                "api_key_uid": api_key_uid,
                "created_at": created_at,
                "user_uid": user_uid,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        api_key_peek = d.pop("api_key_peek")

        api_key_uid = d.pop("api_key_uid")

        created_at = isoparse(d.pop("created_at"))

        user_uid = d.pop("user_uid")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        obj = cls(
            api_key_peek=api_key_peek,
            api_key_uid=api_key_uid,
            created_at=created_at,
            user_uid=user_uid,
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
