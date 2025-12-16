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
    from ..models.prompt_dev_execution_job_status import (
        PromptDevExecutionJobStatus,  # noqa: F401
    )
    from ..models.prompt_dev_execution_version_response_xuid_to_response import (
        PromptDevExecutionVersionResponseXuidToResponse,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptDevExecutionVersionResponse")


@attrs.define
class PromptDevExecutionVersionResponse:
    """
    Attributes:
        execution_job (PromptDevExecutionJobStatus):
        xuid_to_response (PromptDevExecutionVersionResponseXuidToResponse):
    """

    execution_job: "PromptDevExecutionJobStatus"
    xuid_to_response: "PromptDevExecutionVersionResponseXuidToResponse"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_dev_execution_job_status import (
            PromptDevExecutionJobStatus,  # noqa: F401
        )
        from ..models.prompt_dev_execution_version_response_xuid_to_response import (
            PromptDevExecutionVersionResponseXuidToResponse,  # noqa: F401
        )
        # fmt: on
        execution_job = self.execution_job.to_dict()
        xuid_to_response = self.xuid_to_response.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_job": execution_job,
                "xuid_to_response": xuid_to_response,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_dev_execution_job_status import (
            PromptDevExecutionJobStatus,  # noqa: F401
        )
        from ..models.prompt_dev_execution_version_response_xuid_to_response import (
            PromptDevExecutionVersionResponseXuidToResponse,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        execution_job = PromptDevExecutionJobStatus.from_dict(d.pop("execution_job"))

        xuid_to_response = PromptDevExecutionVersionResponseXuidToResponse.from_dict(
            d.pop("xuid_to_response")
        )

        obj = cls(
            execution_job=execution_job,
            xuid_to_response=xuid_to_response,
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
