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

T = TypeVar("T", bound="OpenAISecretsConfig")


@attrs.define
class OpenAISecretsConfig:
    """
    Attributes:
        provider (Literal['openai']):
        openai_api_key (Union[Unset, str]):
    """

    provider: Literal["openai"]
    openai_api_key: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider = self.provider
        openai_api_key = self.openai_api_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if openai_api_key is not UNSET:
            field_dict["openai_api_key"] = openai_api_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provider = d.pop("provider")

        _openai_api_key = d.pop("openai_api_key", UNSET)
        openai_api_key = UNSET if _openai_api_key is None else _openai_api_key

        obj = cls(
            provider=provider,
            openai_api_key=openai_api_key,
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
