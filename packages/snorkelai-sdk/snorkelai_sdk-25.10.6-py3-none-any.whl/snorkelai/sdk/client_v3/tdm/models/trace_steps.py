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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.trace_steps_metadata import TraceStepsMetadata  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="TraceSteps")


@attrs.define
class TraceSteps:
    """
    Attributes:
        context_uid (Union[int, str]):
        depth (int):
        metadata (TraceStepsMetadata):
        step_id (str):
        step_type (str):
        value (str):
        contained_in_filter (Union[Unset, bool]):
        parent_step_id (Union[Unset, str]):
        substeps (Union[Unset, List['TraceSteps']]):
    """

    context_uid: Union[int, str]
    depth: int
    metadata: "TraceStepsMetadata"
    step_id: str
    step_type: str
    value: str
    contained_in_filter: Union[Unset, bool] = UNSET
    parent_step_id: Union[Unset, str] = UNSET
    substeps: Union[Unset, List["TraceSteps"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.trace_steps_metadata import TraceStepsMetadata  # noqa: F401
        # fmt: on
        context_uid: Union[int, str]
        context_uid = self.context_uid
        depth = self.depth
        metadata = self.metadata.to_dict()
        step_id = self.step_id
        step_type = self.step_type
        value = self.value
        contained_in_filter = self.contained_in_filter
        parent_step_id = self.parent_step_id
        substeps: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.substeps, Unset):
            substeps = []
            for substeps_item_data in self.substeps:
                substeps_item = substeps_item_data.to_dict()
                substeps.append(substeps_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "context_uid": context_uid,
                "depth": depth,
                "metadata": metadata,
                "step_id": step_id,
                "step_type": step_type,
                "value": value,
            }
        )
        if contained_in_filter is not UNSET:
            field_dict["contained_in_filter"] = contained_in_filter
        if parent_step_id is not UNSET:
            field_dict["parent_step_id"] = parent_step_id
        if substeps is not UNSET:
            field_dict["substeps"] = substeps

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.trace_steps_metadata import TraceStepsMetadata  # noqa: F401
        # fmt: on
        d = src_dict.copy()

        def _parse_context_uid(data: object) -> Union[int, str]:
            return cast(Union[int, str], data)

        context_uid = _parse_context_uid(d.pop("context_uid"))

        depth = d.pop("depth")

        metadata = TraceStepsMetadata.from_dict(d.pop("metadata"))

        step_id = d.pop("step_id")

        step_type = d.pop("step_type")

        value = d.pop("value")

        _contained_in_filter = d.pop("contained_in_filter", UNSET)
        contained_in_filter = (
            UNSET if _contained_in_filter is None else _contained_in_filter
        )

        _parent_step_id = d.pop("parent_step_id", UNSET)
        parent_step_id = UNSET if _parent_step_id is None else _parent_step_id

        _substeps = d.pop("substeps", UNSET)
        substeps = []
        _substeps = UNSET if _substeps is None else _substeps
        for substeps_item_data in _substeps or []:
            substeps_item = TraceSteps.from_dict(substeps_item_data)

            substeps.append(substeps_item)

        obj = cls(
            context_uid=context_uid,
            depth=depth,
            metadata=metadata,
            step_id=step_id,
            step_type=step_type,
            value=value,
            contained_in_filter=contained_in_filter,
            parent_step_id=parent_step_id,
            substeps=substeps,
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
