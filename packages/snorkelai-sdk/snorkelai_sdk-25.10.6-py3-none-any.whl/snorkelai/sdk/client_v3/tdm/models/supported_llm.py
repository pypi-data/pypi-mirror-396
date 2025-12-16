from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.external_llm_provider import ExternalLLMProvider
from ..models.fm_type import FMType

T = TypeVar("T", bound="SupportedLLM")


@attrs.define
class SupportedLLM:
    """
    Attributes:
        fm_type (FMType):
        model_name (str):
        provider (ExternalLLMProvider):
    """

    fm_type: FMType
    model_name: str
    provider: ExternalLLMProvider
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        fm_type = self.fm_type.value
        model_name = self.model_name
        provider = self.provider.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fm_type": fm_type,
                "model_name": model_name,
                "provider": provider,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fm_type = FMType(d.pop("fm_type"))

        model_name = d.pop("model_name")

        provider = ExternalLLMProvider(d.pop("provider"))

        obj = cls(
            fm_type=fm_type,
            model_name=model_name,
            provider=provider,
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
