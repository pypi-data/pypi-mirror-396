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
    from ..models.gcs_upload_credentials_token import (
        GCSUploadCredentialsToken,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GCSUploadCredentials")


@attrs.define
class GCSUploadCredentials:
    """
    Attributes:
        token (GCSUploadCredentialsToken):
    """

    token: "GCSUploadCredentialsToken"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.gcs_upload_credentials_token import (
            GCSUploadCredentialsToken,  # noqa: F401
        )
        # fmt: on
        token = self.token.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.gcs_upload_credentials_token import (
            GCSUploadCredentialsToken,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        token = GCSUploadCredentialsToken.from_dict(d.pop("token"))

        obj = cls(
            token=token,
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
