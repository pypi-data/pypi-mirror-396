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

T = TypeVar("T", bound="SamlIdpSettings")


@attrs.define
class SamlIdpSettings:
    """
    Attributes:
        entity_id (Union[Unset, str]):
        sso_binding (Union[Unset, str]):
        sso_url (Union[Unset, str]):
        x509_cert (Union[Unset, str]):
    """

    entity_id: Union[Unset, str] = UNSET
    sso_binding: Union[Unset, str] = UNSET
    sso_url: Union[Unset, str] = UNSET
    x509_cert: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        entity_id = self.entity_id
        sso_binding = self.sso_binding
        sso_url = self.sso_url
        x509_cert = self.x509_cert

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entity_id is not UNSET:
            field_dict["entity_id"] = entity_id
        if sso_binding is not UNSET:
            field_dict["sso_binding"] = sso_binding
        if sso_url is not UNSET:
            field_dict["sso_url"] = sso_url
        if x509_cert is not UNSET:
            field_dict["x509_cert"] = x509_cert

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _entity_id = d.pop("entity_id", UNSET)
        entity_id = UNSET if _entity_id is None else _entity_id

        _sso_binding = d.pop("sso_binding", UNSET)
        sso_binding = UNSET if _sso_binding is None else _sso_binding

        _sso_url = d.pop("sso_url", UNSET)
        sso_url = UNSET if _sso_url is None else _sso_url

        _x509_cert = d.pop("x509_cert", UNSET)
        x509_cert = UNSET if _x509_cert is None else _x509_cert

        obj = cls(
            entity_id=entity_id,
            sso_binding=sso_binding,
            sso_url=sso_url,
            x509_cert=x509_cert,
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
