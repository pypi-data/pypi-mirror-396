from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="SamlSpSettings")


@attrs.define
class SamlSpSettings:
    """
    Attributes:
        acs_binding (str):
        acs_url (str):
        entity_id (str):
        name_id_format (str):
        signed_response (bool):
        x509_cert (str):
    """

    acs_binding: str
    acs_url: str
    entity_id: str
    name_id_format: str
    signed_response: bool
    x509_cert: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        acs_binding = self.acs_binding
        acs_url = self.acs_url
        entity_id = self.entity_id
        name_id_format = self.name_id_format
        signed_response = self.signed_response
        x509_cert = self.x509_cert

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "acs_binding": acs_binding,
                "acs_url": acs_url,
                "entity_id": entity_id,
                "name_id_format": name_id_format,
                "signed_response": signed_response,
                "x509_cert": x509_cert,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        acs_binding = d.pop("acs_binding")

        acs_url = d.pop("acs_url")

        entity_id = d.pop("entity_id")

        name_id_format = d.pop("name_id_format")

        signed_response = d.pop("signed_response")

        x509_cert = d.pop("x509_cert")

        obj = cls(
            acs_binding=acs_binding,
            acs_url=acs_url,
            entity_id=entity_id,
            name_id_format=name_id_format,
            signed_response=signed_response,
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
