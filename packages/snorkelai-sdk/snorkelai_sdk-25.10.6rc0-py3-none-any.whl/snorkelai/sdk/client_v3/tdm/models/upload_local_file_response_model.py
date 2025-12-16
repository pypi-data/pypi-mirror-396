from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

T = TypeVar("T", bound="UploadLocalFileResponseModel")


@attrs.define
class UploadLocalFileResponseModel:
    """
    Attributes:
        csv_file_path (str):
        file_paths (List[str]):
        resized_file_paths (List[str]):
    """

    csv_file_path: str
    file_paths: List[str]
    resized_file_paths: List[str]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        csv_file_path = self.csv_file_path
        file_paths = self.file_paths

        resized_file_paths = self.resized_file_paths

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "csv_file_path": csv_file_path,
                "file_paths": file_paths,
                "resized_file_paths": resized_file_paths,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        csv_file_path = d.pop("csv_file_path")

        file_paths = cast(List[str], d.pop("file_paths"))

        resized_file_paths = cast(List[str], d.pop("resized_file_paths"))

        obj = cls(
            csv_file_path=csv_file_path,
            file_paths=file_paths,
            resized_file_paths=resized_file_paths,
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
