import json
from io import BytesIO
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="BodyUploadLocalStaticAssetUploadLocalFilesPost")


@attrs.define
class BodyUploadLocalStaticAssetUploadLocalFilesPost:
    """
    Attributes:
        files (List[File]):
        target_path (Union[Unset, str]):  Default: ''.
    """

    files: List[File]
    target_path: Union[Unset, str] = ""
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        target_path = self.target_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if target_path is not UNSET:
            field_dict["target_path"] = target_path

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        _temp_files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            _temp_files.append(files_item)
        files = (None, json.dumps(_temp_files).encode(), "application/json")

        target_path = (
            self.target_path
            if isinstance(self.target_path, Unset)
            else (None, str(self.target_path).encode(), "text/plain")
        )

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                key: (None, str(value).encode(), "text/plain")
                for key, value in self.additional_properties.items()
            }
        )
        field_dict.update(
            {
                "files": files,
            }
        )
        if target_path is not UNSET:
            field_dict["target_path"] = target_path

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        _target_path = d.pop("target_path", UNSET)
        target_path = UNSET if _target_path is None else _target_path

        obj = cls(
            files=files,
            target_path=target_path,
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
