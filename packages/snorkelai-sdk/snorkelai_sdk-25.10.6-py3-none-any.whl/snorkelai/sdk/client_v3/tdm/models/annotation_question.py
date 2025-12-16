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

from ..models.label_type import LabelType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_question_option import (
        AnnotationQuestionOption,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AnnotationQuestion")


@attrs.define
class AnnotationQuestion:
    """
    Attributes:
        name (str):
        type (LabelType):
        allow_overlapping (Union[Unset, bool]):
        description (Union[Unset, str]):
        iou_agreement_threshold (Union[Unset, float]):
        is_multi_label (Union[Unset, bool]):
        is_required (Union[Unset, bool]):  Default: False.
        is_text_label (Union[Unset, bool]):
        options (Union[Unset, List['AnnotationQuestionOption']]):
        primary_field (Union[Unset, str]):
    """

    name: str
    type: LabelType
    allow_overlapping: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    iou_agreement_threshold: Union[Unset, float] = UNSET
    is_multi_label: Union[Unset, bool] = UNSET
    is_required: Union[Unset, bool] = False
    is_text_label: Union[Unset, bool] = UNSET
    options: Union[Unset, List["AnnotationQuestionOption"]] = UNSET
    primary_field: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_question_option import (
            AnnotationQuestionOption,  # noqa: F401
        )
        # fmt: on
        name = self.name
        type = self.type.value
        allow_overlapping = self.allow_overlapping
        description = self.description
        iou_agreement_threshold = self.iou_agreement_threshold
        is_multi_label = self.is_multi_label
        is_required = self.is_required
        is_text_label = self.is_text_label
        options: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.options, Unset):
            options = []
            for options_item_data in self.options:
                options_item = options_item_data.to_dict()
                options.append(options_item)

        primary_field = self.primary_field

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )
        if allow_overlapping is not UNSET:
            field_dict["allow_overlapping"] = allow_overlapping
        if description is not UNSET:
            field_dict["description"] = description
        if iou_agreement_threshold is not UNSET:
            field_dict["iou_agreement_threshold"] = iou_agreement_threshold
        if is_multi_label is not UNSET:
            field_dict["is_multi_label"] = is_multi_label
        if is_required is not UNSET:
            field_dict["is_required"] = is_required
        if is_text_label is not UNSET:
            field_dict["is_text_label"] = is_text_label
        if options is not UNSET:
            field_dict["options"] = options
        if primary_field is not UNSET:
            field_dict["primary_field"] = primary_field

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_question_option import (
            AnnotationQuestionOption,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        name = d.pop("name")

        type = LabelType(d.pop("type"))

        _allow_overlapping = d.pop("allow_overlapping", UNSET)
        allow_overlapping = UNSET if _allow_overlapping is None else _allow_overlapping

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _iou_agreement_threshold = d.pop("iou_agreement_threshold", UNSET)
        iou_agreement_threshold = (
            UNSET if _iou_agreement_threshold is None else _iou_agreement_threshold
        )

        _is_multi_label = d.pop("is_multi_label", UNSET)
        is_multi_label = UNSET if _is_multi_label is None else _is_multi_label

        _is_required = d.pop("is_required", UNSET)
        is_required = UNSET if _is_required is None else _is_required

        _is_text_label = d.pop("is_text_label", UNSET)
        is_text_label = UNSET if _is_text_label is None else _is_text_label

        _options = d.pop("options", UNSET)
        options = []
        _options = UNSET if _options is None else _options
        for options_item_data in _options or []:
            options_item = AnnotationQuestionOption.from_dict(options_item_data)

            options.append(options_item)

        _primary_field = d.pop("primary_field", UNSET)
        primary_field = UNSET if _primary_field is None else _primary_field

        obj = cls(
            name=name,
            type=type,
            allow_overlapping=allow_overlapping,
            description=description,
            iou_agreement_threshold=iou_agreement_threshold,
            is_multi_label=is_multi_label,
            is_required=is_required,
            is_text_label=is_text_label,
            options=options,
            primary_field=primary_field,
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
