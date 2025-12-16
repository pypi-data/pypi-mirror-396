import datetime
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
from dateutil.parser import isoparse

from ..models.criteria_template_state import CriteriaTemplateState
from ..models.evaluator_template_type import EvaluatorTemplateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.criteria_template_label_map import (
        CriteriaTemplateLabelMap,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CriteriaTemplate")


@attrs.define
class CriteriaTemplate:
    """
    Attributes:
        created_by (int):
        criteria_description (str):
        criteria_name (str):
        criteria_template_description (str):
        criteria_template_name (str):
        evaluator_template_uid (int):
        label_map (CriteriaTemplateLabelMap):
        requires_rationale (bool):
        saved_from_criteria_uid (int):
        state (CriteriaTemplateState):
        type (EvaluatorTemplateType):
        workspace_uid (int):
        created_at (Union[Unset, datetime.datetime]):
        criteria_template_uid (Union[Unset, int]):
    """

    created_by: int
    criteria_description: str
    criteria_name: str
    criteria_template_description: str
    criteria_template_name: str
    evaluator_template_uid: int
    label_map: "CriteriaTemplateLabelMap"
    requires_rationale: bool
    saved_from_criteria_uid: int
    state: CriteriaTemplateState
    type: EvaluatorTemplateType
    workspace_uid: int
    created_at: Union[Unset, datetime.datetime] = UNSET
    criteria_template_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.criteria_template_label_map import (
            CriteriaTemplateLabelMap,  # noqa: F401
        )
        # fmt: on
        created_by = self.created_by
        criteria_description = self.criteria_description
        criteria_name = self.criteria_name
        criteria_template_description = self.criteria_template_description
        criteria_template_name = self.criteria_template_name
        evaluator_template_uid = self.evaluator_template_uid
        label_map = self.label_map.to_dict()
        requires_rationale = self.requires_rationale
        saved_from_criteria_uid = self.saved_from_criteria_uid
        state = self.state.value
        type = self.type.value
        workspace_uid = self.workspace_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        criteria_template_uid = self.criteria_template_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_by": created_by,
                "criteria_description": criteria_description,
                "criteria_name": criteria_name,
                "criteria_template_description": criteria_template_description,
                "criteria_template_name": criteria_template_name,
                "evaluator_template_uid": evaluator_template_uid,
                "label_map": label_map,
                "requires_rationale": requires_rationale,
                "saved_from_criteria_uid": saved_from_criteria_uid,
                "state": state,
                "type": type,
                "workspace_uid": workspace_uid,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if criteria_template_uid is not UNSET:
            field_dict["criteria_template_uid"] = criteria_template_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.criteria_template_label_map import (
            CriteriaTemplateLabelMap,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_by = d.pop("created_by")

        criteria_description = d.pop("criteria_description")

        criteria_name = d.pop("criteria_name")

        criteria_template_description = d.pop("criteria_template_description")

        criteria_template_name = d.pop("criteria_template_name")

        evaluator_template_uid = d.pop("evaluator_template_uid")

        label_map = CriteriaTemplateLabelMap.from_dict(d.pop("label_map"))

        requires_rationale = d.pop("requires_rationale")

        saved_from_criteria_uid = d.pop("saved_from_criteria_uid")

        state = CriteriaTemplateState(d.pop("state"))

        type = EvaluatorTemplateType(d.pop("type"))

        workspace_uid = d.pop("workspace_uid")

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _criteria_template_uid = d.pop("criteria_template_uid", UNSET)
        criteria_template_uid = (
            UNSET if _criteria_template_uid is None else _criteria_template_uid
        )

        obj = cls(
            created_by=created_by,
            criteria_description=criteria_description,
            criteria_name=criteria_name,
            criteria_template_description=criteria_template_description,
            criteria_template_name=criteria_template_name,
            evaluator_template_uid=evaluator_template_uid,
            label_map=label_map,
            requires_rationale=requires_rationale,
            saved_from_criteria_uid=saved_from_criteria_uid,
            state=state,
            type=type,
            workspace_uid=workspace_uid,
            created_at=created_at,
            criteria_template_uid=criteria_template_uid,
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
