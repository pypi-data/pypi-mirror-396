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
    from ..models.create_benchmark_payload_metadata import (
        CreateBenchmarkPayloadMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateBenchmarkPayload")


@attrs.define
class CreateBenchmarkPayload:
    """
    Attributes:
        input_dataset_uid (int):
        name (str):
        workspace_uid (int):
        description (Union[Unset, str]):
        metadata (Union[Unset, CreateBenchmarkPayloadMetadata]):
    """

    input_dataset_uid: int
    name: str
    workspace_uid: int
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, "CreateBenchmarkPayloadMetadata"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_benchmark_payload_metadata import (
            CreateBenchmarkPayloadMetadata,  # noqa: F401
        )
        # fmt: on
        input_dataset_uid = self.input_dataset_uid
        name = self.name
        workspace_uid = self.workspace_uid
        description = self.description
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_dataset_uid": input_dataset_uid,
                "name": name,
                "workspace_uid": workspace_uid,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_benchmark_payload_metadata import (
            CreateBenchmarkPayloadMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        input_dataset_uid = d.pop("input_dataset_uid")

        name = d.pop("name")

        workspace_uid = d.pop("workspace_uid")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, CreateBenchmarkPayloadMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateBenchmarkPayloadMetadata.from_dict(_metadata)

        obj = cls(
            input_dataset_uid=input_dataset_uid,
            name=name,
            workspace_uid=workspace_uid,
            description=description,
            metadata=metadata,
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
