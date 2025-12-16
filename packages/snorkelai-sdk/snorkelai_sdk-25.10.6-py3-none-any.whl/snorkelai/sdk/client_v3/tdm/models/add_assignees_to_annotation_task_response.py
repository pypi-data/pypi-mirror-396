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
    from ..models.datapoint_assignee_params import DatapointAssigneeParams  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AddAssigneesToAnnotationTaskResponse")


@attrs.define
class AddAssigneesToAnnotationTaskResponse:
    """Response model for adding assignees to datapoints.

    Attributes:
        failed_assignments (Union[Unset, List['DatapointAssigneeParams']]):
        successful_assignments (Union[Unset, List['DatapointAssigneeParams']]):
    """

    failed_assignments: Union[Unset, List["DatapointAssigneeParams"]] = UNSET
    successful_assignments: Union[Unset, List["DatapointAssigneeParams"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.datapoint_assignee_params import (
            DatapointAssigneeParams,  # noqa: F401
        )
        # fmt: on
        failed_assignments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.failed_assignments, Unset):
            failed_assignments = []
            for failed_assignments_item_data in self.failed_assignments:
                failed_assignments_item = failed_assignments_item_data.to_dict()
                failed_assignments.append(failed_assignments_item)

        successful_assignments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.successful_assignments, Unset):
            successful_assignments = []
            for successful_assignments_item_data in self.successful_assignments:
                successful_assignments_item = successful_assignments_item_data.to_dict()
                successful_assignments.append(successful_assignments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if failed_assignments is not UNSET:
            field_dict["failed_assignments"] = failed_assignments
        if successful_assignments is not UNSET:
            field_dict["successful_assignments"] = successful_assignments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.datapoint_assignee_params import (
            DatapointAssigneeParams,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _failed_assignments = d.pop("failed_assignments", UNSET)
        failed_assignments = []
        _failed_assignments = (
            UNSET if _failed_assignments is None else _failed_assignments
        )
        for failed_assignments_item_data in _failed_assignments or []:
            failed_assignments_item = DatapointAssigneeParams.from_dict(
                failed_assignments_item_data
            )

            failed_assignments.append(failed_assignments_item)

        _successful_assignments = d.pop("successful_assignments", UNSET)
        successful_assignments = []
        _successful_assignments = (
            UNSET if _successful_assignments is None else _successful_assignments
        )
        for successful_assignments_item_data in _successful_assignments or []:
            successful_assignments_item = DatapointAssigneeParams.from_dict(
                successful_assignments_item_data
            )

            successful_assignments.append(successful_assignments_item)

        obj = cls(
            failed_assignments=failed_assignments,
            successful_assignments=successful_assignments,
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
