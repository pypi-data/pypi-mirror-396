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
    from ..models.saml_idp_settings import SamlIdpSettings  # noqa: F401
    from ..models.saml_sp_settings import SamlSpSettings  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SamlSettingsResponse")


@attrs.define
class SamlSettingsResponse:
    """
    Attributes:
        idp_settings (SamlIdpSettings):
        sp_settings (SamlSpSettings):
    """

    idp_settings: "SamlIdpSettings"
    sp_settings: "SamlSpSettings"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.saml_idp_settings import SamlIdpSettings  # noqa: F401
        from ..models.saml_sp_settings import SamlSpSettings  # noqa: F401
        # fmt: on
        idp_settings = self.idp_settings.to_dict()
        sp_settings = self.sp_settings.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "idp_settings": idp_settings,
                "sp_settings": sp_settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.saml_idp_settings import SamlIdpSettings  # noqa: F401
        from ..models.saml_sp_settings import SamlSpSettings  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        idp_settings = SamlIdpSettings.from_dict(d.pop("idp_settings"))

        sp_settings = SamlSpSettings.from_dict(d.pop("sp_settings"))

        obj = cls(
            idp_settings=idp_settings,
            sp_settings=sp_settings,
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
