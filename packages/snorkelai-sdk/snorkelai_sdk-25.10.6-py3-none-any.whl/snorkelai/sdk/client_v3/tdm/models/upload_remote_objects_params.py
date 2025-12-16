from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..models.asset_upload_type import AssetUploadType
from ..models.remote_storage_type import RemoteStorageType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.remote_upload_credentials import RemoteUploadCredentials  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="UploadRemoteObjectsParams")


@attrs.define
class UploadRemoteObjectsParams:
    """
    Attributes:
        bucket_type (RemoteStorageType):
        file_type (AssetUploadType):
        target_path (str):
        bucket_files (Union[Unset, List[str]]):
        credentials (Union[Unset, RemoteUploadCredentials]):
        max_num_processes (Union[Unset, int]):  Default: 4.
        overwrite_existing (Union[Unset, bool]):  Default: True.
        page_size (Union[Unset, int]):  Default: 5000.
        remote_path (Union[Unset, str]):
    """

    bucket_type: RemoteStorageType
    file_type: AssetUploadType
    target_path: str
    bucket_files: Union[Unset, List[str]] = UNSET
    credentials: Union[Unset, "RemoteUploadCredentials"] = UNSET
    max_num_processes: Union[Unset, int] = 4
    overwrite_existing: Union[Unset, bool] = True
    page_size: Union[Unset, int] = 5000
    remote_path: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.remote_upload_credentials import (
            RemoteUploadCredentials,  # noqa: F401
        )
        # fmt: on
        bucket_type = self.bucket_type.value
        file_type = self.file_type.value
        target_path = self.target_path
        bucket_files: Union[Unset, List[str]] = UNSET
        if not isinstance(self.bucket_files, Unset):
            bucket_files = self.bucket_files

        credentials: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.credentials, Unset):
            credentials = self.credentials.to_dict()
        max_num_processes = self.max_num_processes
        overwrite_existing = self.overwrite_existing
        page_size = self.page_size
        remote_path = self.remote_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucket_type": bucket_type,
                "file_type": file_type,
                "target_path": target_path,
            }
        )
        if bucket_files is not UNSET:
            field_dict["bucket_files"] = bucket_files
        if credentials is not UNSET:
            field_dict["credentials"] = credentials
        if max_num_processes is not UNSET:
            field_dict["max_num_processes"] = max_num_processes
        if overwrite_existing is not UNSET:
            field_dict["overwrite_existing"] = overwrite_existing
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if remote_path is not UNSET:
            field_dict["remote_path"] = remote_path

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.remote_upload_credentials import (
            RemoteUploadCredentials,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        bucket_type = RemoteStorageType(d.pop("bucket_type"))

        file_type = AssetUploadType(d.pop("file_type"))

        target_path = d.pop("target_path")

        _bucket_files = d.pop("bucket_files", UNSET)
        bucket_files = cast(
            List[str], UNSET if _bucket_files is None else _bucket_files
        )

        _credentials = d.pop("credentials", UNSET)
        _credentials = UNSET if _credentials is None else _credentials
        credentials: Union[Unset, RemoteUploadCredentials]
        if isinstance(_credentials, Unset):
            credentials = UNSET
        else:
            credentials = RemoteUploadCredentials.from_dict(_credentials)

        _max_num_processes = d.pop("max_num_processes", UNSET)
        max_num_processes = UNSET if _max_num_processes is None else _max_num_processes

        _overwrite_existing = d.pop("overwrite_existing", UNSET)
        overwrite_existing = (
            UNSET if _overwrite_existing is None else _overwrite_existing
        )

        _page_size = d.pop("page_size", UNSET)
        page_size = UNSET if _page_size is None else _page_size

        _remote_path = d.pop("remote_path", UNSET)
        remote_path = UNSET if _remote_path is None else _remote_path

        obj = cls(
            bucket_type=bucket_type,
            file_type=file_type,
            target_path=target_path,
            bucket_files=bucket_files,
            credentials=credentials,
            max_num_processes=max_num_processes,
            overwrite_existing=overwrite_existing,
            page_size=page_size,
            remote_path=remote_path,
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
