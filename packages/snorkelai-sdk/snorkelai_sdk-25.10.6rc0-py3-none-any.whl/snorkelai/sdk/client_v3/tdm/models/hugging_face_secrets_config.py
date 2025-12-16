from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="HuggingFaceSecretsConfig")


@attrs.define
class HuggingFaceSecretsConfig:
    """
    Attributes:
        provider (Literal['huggingface']):
        huggingfaceinferenceapi_token (Union[Unset, str]):
    """

    provider: Literal["huggingface"]
    huggingfaceinferenceapi_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider = self.provider
        huggingfaceinferenceapi_token = self.huggingfaceinferenceapi_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if huggingfaceinferenceapi_token is not UNSET:
            field_dict["huggingface::inference::api_token"] = (
                huggingfaceinferenceapi_token
            )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provider = d.pop("provider")

        _huggingfaceinferenceapi_token = d.pop(
            "huggingface::inference::api_token", UNSET
        )
        huggingfaceinferenceapi_token = (
            UNSET
            if _huggingfaceinferenceapi_token is None
            else _huggingfaceinferenceapi_token
        )

        obj = cls(
            provider=provider,
            huggingfaceinferenceapi_token=huggingfaceinferenceapi_token,
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
