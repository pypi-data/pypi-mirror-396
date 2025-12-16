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

from ..models.criteria_template_state import CriteriaTemplateState
from ..models.evaluator_template_type import EvaluatorTemplateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.update_criteria_template_request_label_map import (
        UpdateCriteriaTemplateRequestLabelMap,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdateCriteriaTemplateRequest")


@attrs.define
class UpdateCriteriaTemplateRequest:
    """
    Attributes:
        criteria_description (Union[Unset, str]):
        criteria_name (Union[Unset, str]):
        criteria_template_description (Union[Unset, str]):
        criteria_template_name (Union[Unset, str]):
        label_map (Union[Unset, UpdateCriteriaTemplateRequestLabelMap]):
        requires_rationale (Union[Unset, bool]):
        saved_from_criteria_uid (Union[Unset, int]):
        state (Union[Unset, CriteriaTemplateState]):
        type (Union[Unset, EvaluatorTemplateType]):
    """

    criteria_description: Union[Unset, str] = UNSET
    criteria_name: Union[Unset, str] = UNSET
    criteria_template_description: Union[Unset, str] = UNSET
    criteria_template_name: Union[Unset, str] = UNSET
    label_map: Union[Unset, "UpdateCriteriaTemplateRequestLabelMap"] = UNSET
    requires_rationale: Union[Unset, bool] = UNSET
    saved_from_criteria_uid: Union[Unset, int] = UNSET
    state: Union[Unset, CriteriaTemplateState] = UNSET
    type: Union[Unset, EvaluatorTemplateType] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_criteria_template_request_label_map import (
            UpdateCriteriaTemplateRequestLabelMap,  # noqa: F401
        )
        # fmt: on
        criteria_description = self.criteria_description
        criteria_name = self.criteria_name
        criteria_template_description = self.criteria_template_description
        criteria_template_name = self.criteria_template_name
        label_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_map, Unset):
            label_map = self.label_map.to_dict()
        requires_rationale = self.requires_rationale
        saved_from_criteria_uid = self.saved_from_criteria_uid
        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if criteria_description is not UNSET:
            field_dict["criteria_description"] = criteria_description
        if criteria_name is not UNSET:
            field_dict["criteria_name"] = criteria_name
        if criteria_template_description is not UNSET:
            field_dict["criteria_template_description"] = criteria_template_description
        if criteria_template_name is not UNSET:
            field_dict["criteria_template_name"] = criteria_template_name
        if label_map is not UNSET:
            field_dict["label_map"] = label_map
        if requires_rationale is not UNSET:
            field_dict["requires_rationale"] = requires_rationale
        if saved_from_criteria_uid is not UNSET:
            field_dict["saved_from_criteria_uid"] = saved_from_criteria_uid
        if state is not UNSET:
            field_dict["state"] = state
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_criteria_template_request_label_map import (
            UpdateCriteriaTemplateRequestLabelMap,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _criteria_description = d.pop("criteria_description", UNSET)
        criteria_description = (
            UNSET if _criteria_description is None else _criteria_description
        )

        _criteria_name = d.pop("criteria_name", UNSET)
        criteria_name = UNSET if _criteria_name is None else _criteria_name

        _criteria_template_description = d.pop("criteria_template_description", UNSET)
        criteria_template_description = (
            UNSET
            if _criteria_template_description is None
            else _criteria_template_description
        )

        _criteria_template_name = d.pop("criteria_template_name", UNSET)
        criteria_template_name = (
            UNSET if _criteria_template_name is None else _criteria_template_name
        )

        _label_map = d.pop("label_map", UNSET)
        _label_map = UNSET if _label_map is None else _label_map
        label_map: Union[Unset, UpdateCriteriaTemplateRequestLabelMap]
        if isinstance(_label_map, Unset):
            label_map = UNSET
        else:
            label_map = UpdateCriteriaTemplateRequestLabelMap.from_dict(_label_map)

        _requires_rationale = d.pop("requires_rationale", UNSET)
        requires_rationale = (
            UNSET if _requires_rationale is None else _requires_rationale
        )

        _saved_from_criteria_uid = d.pop("saved_from_criteria_uid", UNSET)
        saved_from_criteria_uid = (
            UNSET if _saved_from_criteria_uid is None else _saved_from_criteria_uid
        )

        _state = d.pop("state", UNSET)
        _state = UNSET if _state is None else _state
        state: Union[Unset, CriteriaTemplateState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = CriteriaTemplateState(_state)

        _type = d.pop("type", UNSET)
        _type = UNSET if _type is None else _type
        type: Union[Unset, EvaluatorTemplateType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EvaluatorTemplateType(_type)

        obj = cls(
            criteria_description=criteria_description,
            criteria_name=criteria_name,
            criteria_template_description=criteria_template_description,
            criteria_template_name=criteria_template_name,
            label_map=label_map,
            requires_rationale=requires_rationale,
            saved_from_criteria_uid=saved_from_criteria_uid,
            state=state,
            type=type,
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
