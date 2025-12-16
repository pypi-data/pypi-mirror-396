from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.gcs_upload_credentials import GCSUploadCredentials  # noqa: F401
    from ..models.s3_upload_credentials import S3UploadCredentials  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="RemoteUploadCredentials")


@attrs.define
class RemoteUploadCredentials:
    """
    Attributes:
        gcs (Union[Unset, GCSUploadCredentials]):
        s3 (Union[Unset, S3UploadCredentials]):
    """

    gcs: Union[Unset, "GCSUploadCredentials"] = UNSET
    s3: Union[Unset, "S3UploadCredentials"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.gcs_upload_credentials import GCSUploadCredentials  # noqa: F401
        from ..models.s3_upload_credentials import S3UploadCredentials  # noqa: F401
        # fmt: on
        gcs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.gcs, Unset):
            gcs = self.gcs.to_dict()
        s3: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.s3, Unset):
            s3 = self.s3.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gcs is not UNSET:
            field_dict["gcs"] = gcs
        if s3 is not UNSET:
            field_dict["s3"] = s3

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.gcs_upload_credentials import GCSUploadCredentials  # noqa: F401
        from ..models.s3_upload_credentials import S3UploadCredentials  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _gcs = d.pop("gcs", UNSET)
        _gcs = UNSET if _gcs is None else _gcs
        gcs: Union[Unset, GCSUploadCredentials]
        if isinstance(_gcs, Unset):
            gcs = UNSET
        else:
            gcs = GCSUploadCredentials.from_dict(_gcs)

        _s3 = d.pop("s3", UNSET)
        _s3 = UNSET if _s3 is None else _s3
        s3: Union[Unset, S3UploadCredentials]
        if isinstance(_s3, Unset):
            s3 = UNSET
        else:
            s3 = S3UploadCredentials.from_dict(_s3)

        obj = cls(
            gcs=gcs,
            s3=s3,
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
