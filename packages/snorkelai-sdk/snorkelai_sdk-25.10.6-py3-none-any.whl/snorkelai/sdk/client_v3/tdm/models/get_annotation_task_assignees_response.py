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
    from ..models.get_annotation_task_assignees_response_assignments import (
        GetAnnotationTaskAssigneesResponseAssignments,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GetAnnotationTaskAssigneesResponse")


@attrs.define
class GetAnnotationTaskAssigneesResponse:
    """Response model for viewing all datapoint assignments.

    Attributes:
        assignments (Union[Unset, GetAnnotationTaskAssigneesResponseAssignments]):
    """

    assignments: Union[Unset, "GetAnnotationTaskAssigneesResponseAssignments"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.get_annotation_task_assignees_response_assignments import (
            GetAnnotationTaskAssigneesResponseAssignments,  # noqa: F401
        )
        # fmt: on
        assignments: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.assignments, Unset):
            assignments = self.assignments.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignments is not UNSET:
            field_dict["assignments"] = assignments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.get_annotation_task_assignees_response_assignments import (
            GetAnnotationTaskAssigneesResponseAssignments,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _assignments = d.pop("assignments", UNSET)
        _assignments = UNSET if _assignments is None else _assignments
        assignments: Union[Unset, GetAnnotationTaskAssigneesResponseAssignments]
        if isinstance(_assignments, Unset):
            assignments = UNSET
        else:
            assignments = GetAnnotationTaskAssigneesResponseAssignments.from_dict(
                _assignments
            )

        obj = cls(
            assignments=assignments,
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
