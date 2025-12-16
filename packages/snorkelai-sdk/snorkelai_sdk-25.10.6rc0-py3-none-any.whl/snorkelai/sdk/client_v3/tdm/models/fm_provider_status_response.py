from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.external_llm_provider import ExternalLLMProvider

T = TypeVar("T", bound="FMProviderStatusResponse")


@attrs.define
class FMProviderStatusResponse:
    """Response model for FM provider status endpoint

    Attributes:
        description (str):
        is_operational (bool):
        provider (ExternalLLMProvider):
        status_url (str):
    """

    description: str
    is_operational: bool
    provider: ExternalLLMProvider
    status_url: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        description = self.description
        is_operational = self.is_operational
        provider = self.provider.value
        status_url = self.status_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "is_operational": is_operational,
                "provider": provider,
                "status_url": status_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        description = d.pop("description")

        is_operational = d.pop("is_operational")

        provider = ExternalLLMProvider(d.pop("provider"))

        status_url = d.pop("status_url")

        obj = cls(
            description=description,
            is_operational=is_operational,
            provider=provider,
            status_url=status_url,
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
