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

from ..models.evaluator_template_type import EvaluatorTemplateType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.save_criteria_template_label_map import (
        SaveCriteriaTemplateLabelMap,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SaveCriteriaTemplate")


@attrs.define
class SaveCriteriaTemplate:
    """
    Attributes:
        criteria_name (str):
        criteria_template_name (str):
        label_map (SaveCriteriaTemplateLabelMap):
        requires_rationale (bool):
        criteria_description (Union[Unset, str]):
        criteria_template_description (Union[Unset, str]):
        evaluator_template_uid (Union[Unset, int]):
        saved_from_criteria_uid (Union[Unset, int]):
        type (Union[Unset, EvaluatorTemplateType]):
    """

    criteria_name: str
    criteria_template_name: str
    label_map: "SaveCriteriaTemplateLabelMap"
    requires_rationale: bool
    criteria_description: Union[Unset, str] = UNSET
    criteria_template_description: Union[Unset, str] = UNSET
    evaluator_template_uid: Union[Unset, int] = UNSET
    saved_from_criteria_uid: Union[Unset, int] = UNSET
    type: Union[Unset, EvaluatorTemplateType] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.save_criteria_template_label_map import (
            SaveCriteriaTemplateLabelMap,  # noqa: F401
        )
        # fmt: on
        criteria_name = self.criteria_name
        criteria_template_name = self.criteria_template_name
        label_map = self.label_map.to_dict()
        requires_rationale = self.requires_rationale
        criteria_description = self.criteria_description
        criteria_template_description = self.criteria_template_description
        evaluator_template_uid = self.evaluator_template_uid
        saved_from_criteria_uid = self.saved_from_criteria_uid
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "criteria_name": criteria_name,
                "criteria_template_name": criteria_template_name,
                "label_map": label_map,
                "requires_rationale": requires_rationale,
            }
        )
        if criteria_description is not UNSET:
            field_dict["criteria_description"] = criteria_description
        if criteria_template_description is not UNSET:
            field_dict["criteria_template_description"] = criteria_template_description
        if evaluator_template_uid is not UNSET:
            field_dict["evaluator_template_uid"] = evaluator_template_uid
        if saved_from_criteria_uid is not UNSET:
            field_dict["saved_from_criteria_uid"] = saved_from_criteria_uid
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.save_criteria_template_label_map import (
            SaveCriteriaTemplateLabelMap,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        criteria_name = d.pop("criteria_name")

        criteria_template_name = d.pop("criteria_template_name")

        label_map = SaveCriteriaTemplateLabelMap.from_dict(d.pop("label_map"))

        requires_rationale = d.pop("requires_rationale")

        _criteria_description = d.pop("criteria_description", UNSET)
        criteria_description = (
            UNSET if _criteria_description is None else _criteria_description
        )

        _criteria_template_description = d.pop("criteria_template_description", UNSET)
        criteria_template_description = (
            UNSET
            if _criteria_template_description is None
            else _criteria_template_description
        )

        _evaluator_template_uid = d.pop("evaluator_template_uid", UNSET)
        evaluator_template_uid = (
            UNSET if _evaluator_template_uid is None else _evaluator_template_uid
        )

        _saved_from_criteria_uid = d.pop("saved_from_criteria_uid", UNSET)
        saved_from_criteria_uid = (
            UNSET if _saved_from_criteria_uid is None else _saved_from_criteria_uid
        )

        _type = d.pop("type", UNSET)
        _type = UNSET if _type is None else _type
        type: Union[Unset, EvaluatorTemplateType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = EvaluatorTemplateType(_type)

        obj = cls(
            criteria_name=criteria_name,
            criteria_template_name=criteria_template_name,
            label_map=label_map,
            requires_rationale=requires_rationale,
            criteria_description=criteria_description,
            criteria_template_description=criteria_template_description,
            evaluator_template_uid=evaluator_template_uid,
            saved_from_criteria_uid=saved_from_criteria_uid,
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
