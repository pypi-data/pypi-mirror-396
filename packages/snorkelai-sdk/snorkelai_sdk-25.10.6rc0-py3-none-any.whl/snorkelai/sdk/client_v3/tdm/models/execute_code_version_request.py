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
    from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ExecuteCodeVersionRequest")


@attrs.define
class ExecuteCodeVersionRequest:
    """
    Attributes:
        code_version_uid (int):
        execution_vds_metadata (ExecutionVDSMetadata):
    """

    code_version_uid: int
    execution_vds_metadata: "ExecutionVDSMetadata"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        code_version_uid = self.code_version_uid
        execution_vds_metadata = self.execution_vds_metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code_version_uid": code_version_uid,
                "execution_vds_metadata": execution_vds_metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        code_version_uid = d.pop("code_version_uid")

        execution_vds_metadata = ExecutionVDSMetadata.from_dict(
            d.pop("execution_vds_metadata")
        )

        obj = cls(
            code_version_uid=code_version_uid,
            execution_vds_metadata=execution_vds_metadata,
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
