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

T = TypeVar("T", bound="AzureMLSecretsConfig")


@attrs.define
class AzureMLSecretsConfig:
    """
    Attributes:
        provider (Literal['azure_ml']):
        azuremlapi_key (Union[Unset, str]):
    """

    provider: Literal["azure_ml"]
    azuremlapi_key: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider = self.provider
        azuremlapi_key = self.azuremlapi_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if azuremlapi_key is not UNSET:
            field_dict["azure::ml::api_key"] = azuremlapi_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provider = d.pop("provider")

        _azuremlapi_key = d.pop("azure::ml::api_key", UNSET)
        azuremlapi_key = UNSET if _azuremlapi_key is None else _azuremlapi_key

        obj = cls(
            provider=provider,
            azuremlapi_key=azuremlapi_key,
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
