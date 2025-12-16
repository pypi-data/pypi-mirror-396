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
    from ..models.account_info import AccountInfo  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LicenseKey")


@attrs.define
class LicenseKey:
    """
    Attributes:
        account_info (AccountInfo):
        signature (str):
    """

    account_info: "AccountInfo"
    signature: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.account_info import AccountInfo  # noqa: F401
        # fmt: on
        account_info = self.account_info.to_dict()
        signature = self.signature

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account_info": account_info,
                "signature": signature,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.account_info import AccountInfo  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        account_info = AccountInfo.from_dict(d.pop("account_info"))

        signature = d.pop("signature")

        obj = cls(
            account_info=account_info,
            signature=signature,
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
