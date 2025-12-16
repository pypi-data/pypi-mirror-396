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
    from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PromptDevStartExecutionRequest")


@attrs.define
class PromptDevStartExecutionRequest:
    """
    Attributes:
        prompt_uid (int):
        filter_options (Union[Unset, ExecutionVDSMetadata]):
    """

    prompt_uid: int
    filter_options: Union[Unset, "ExecutionVDSMetadata"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        prompt_uid = self.prompt_uid
        filter_options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.filter_options, Unset):
            filter_options = self.filter_options.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt_uid": prompt_uid,
            }
        )
        if filter_options is not UNSET:
            field_dict["filter_options"] = filter_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.execution_vds_metadata import ExecutionVDSMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        prompt_uid = d.pop("prompt_uid")

        _filter_options = d.pop("filter_options", UNSET)
        _filter_options = UNSET if _filter_options is None else _filter_options
        filter_options: Union[Unset, ExecutionVDSMetadata]
        if isinstance(_filter_options, Unset):
            filter_options = UNSET
        else:
            filter_options = ExecutionVDSMetadata.from_dict(_filter_options)

        obj = cls(
            prompt_uid=prompt_uid,
            filter_options=filter_options,
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
