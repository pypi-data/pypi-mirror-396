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

from ..models.evaluator_type import EvaluatorType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.evaluator_criteria_config_label_ordinality_by_user_label import (
        EvaluatorCriteriaConfigLabelOrdinalityByUserLabel,  # noqa: F401
    )
    from ..models.evaluator_criteria_config_metadata import (
        EvaluatorCriteriaConfigMetadata,  # noqa: F401
    )
    from ..models.evaluator_criteria_config_output_format import (
        EvaluatorCriteriaConfigOutputFormat,  # noqa: F401
    )
    from ..models.evaluator_criteria_config_raw_label_by_user_label import (
        EvaluatorCriteriaConfigRawLabelByUserLabel,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="EvaluatorCriteriaConfig")


@attrs.define
class EvaluatorCriteriaConfig:
    """Configuration for an evaluator loaded from S3.

    Attributes:
        name (str):
        output_format (EvaluatorCriteriaConfigOutputFormat):
        type (EvaluatorType):
        description (Union[Unset, str]):
        label_ordinality_by_user_label (Union[Unset, EvaluatorCriteriaConfigLabelOrdinalityByUserLabel]):
        metadata (Union[Unset, EvaluatorCriteriaConfigMetadata]):
        model_name (Union[Unset, str]):
        raw_label_by_user_label (Union[Unset, EvaluatorCriteriaConfigRawLabelByUserLabel]):
        system_prompt (Union[Unset, str]):
        user_prompt (Union[Unset, str]):
    """

    name: str
    output_format: "EvaluatorCriteriaConfigOutputFormat"
    type: EvaluatorType
    description: Union[Unset, str] = UNSET
    label_ordinality_by_user_label: Union[
        Unset, "EvaluatorCriteriaConfigLabelOrdinalityByUserLabel"
    ] = UNSET
    metadata: Union[Unset, "EvaluatorCriteriaConfigMetadata"] = UNSET
    model_name: Union[Unset, str] = UNSET
    raw_label_by_user_label: Union[
        Unset, "EvaluatorCriteriaConfigRawLabelByUserLabel"
    ] = UNSET
    system_prompt: Union[Unset, str] = UNSET
    user_prompt: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.evaluator_criteria_config_label_ordinality_by_user_label import (
            EvaluatorCriteriaConfigLabelOrdinalityByUserLabel,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_metadata import (
            EvaluatorCriteriaConfigMetadata,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_output_format import (
            EvaluatorCriteriaConfigOutputFormat,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_raw_label_by_user_label import (
            EvaluatorCriteriaConfigRawLabelByUserLabel,  # noqa: F401
        )
        # fmt: on
        name = self.name
        output_format = self.output_format.to_dict()
        type = self.type.value
        description = self.description
        label_ordinality_by_user_label: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_ordinality_by_user_label, Unset):
            label_ordinality_by_user_label = (
                self.label_ordinality_by_user_label.to_dict()
            )
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        model_name = self.model_name
        raw_label_by_user_label: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.raw_label_by_user_label, Unset):
            raw_label_by_user_label = self.raw_label_by_user_label.to_dict()
        system_prompt = self.system_prompt
        user_prompt = self.user_prompt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "output_format": output_format,
                "type": type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if label_ordinality_by_user_label is not UNSET:
            field_dict["label_ordinality_by_user_label"] = (
                label_ordinality_by_user_label
            )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
        if raw_label_by_user_label is not UNSET:
            field_dict["raw_label_by_user_label"] = raw_label_by_user_label
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if user_prompt is not UNSET:
            field_dict["user_prompt"] = user_prompt

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.evaluator_criteria_config_label_ordinality_by_user_label import (
            EvaluatorCriteriaConfigLabelOrdinalityByUserLabel,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_metadata import (
            EvaluatorCriteriaConfigMetadata,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_output_format import (
            EvaluatorCriteriaConfigOutputFormat,  # noqa: F401
        )
        from ..models.evaluator_criteria_config_raw_label_by_user_label import (
            EvaluatorCriteriaConfigRawLabelByUserLabel,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        name = d.pop("name")

        output_format = EvaluatorCriteriaConfigOutputFormat.from_dict(
            d.pop("output_format")
        )

        type = EvaluatorType(d.pop("type"))

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _label_ordinality_by_user_label = d.pop("label_ordinality_by_user_label", UNSET)
        _label_ordinality_by_user_label = (
            UNSET
            if _label_ordinality_by_user_label is None
            else _label_ordinality_by_user_label
        )
        label_ordinality_by_user_label: Union[
            Unset, EvaluatorCriteriaConfigLabelOrdinalityByUserLabel
        ]
        if isinstance(_label_ordinality_by_user_label, Unset):
            label_ordinality_by_user_label = UNSET
        else:
            label_ordinality_by_user_label = (
                EvaluatorCriteriaConfigLabelOrdinalityByUserLabel.from_dict(
                    _label_ordinality_by_user_label
                )
            )

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, EvaluatorCriteriaConfigMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = EvaluatorCriteriaConfigMetadata.from_dict(_metadata)

        _model_name = d.pop("model_name", UNSET)
        model_name = UNSET if _model_name is None else _model_name

        _raw_label_by_user_label = d.pop("raw_label_by_user_label", UNSET)
        _raw_label_by_user_label = (
            UNSET if _raw_label_by_user_label is None else _raw_label_by_user_label
        )
        raw_label_by_user_label: Union[
            Unset, EvaluatorCriteriaConfigRawLabelByUserLabel
        ]
        if isinstance(_raw_label_by_user_label, Unset):
            raw_label_by_user_label = UNSET
        else:
            raw_label_by_user_label = (
                EvaluatorCriteriaConfigRawLabelByUserLabel.from_dict(
                    _raw_label_by_user_label
                )
            )

        _system_prompt = d.pop("system_prompt", UNSET)
        system_prompt = UNSET if _system_prompt is None else _system_prompt

        _user_prompt = d.pop("user_prompt", UNSET)
        user_prompt = UNSET if _user_prompt is None else _user_prompt

        obj = cls(
            name=name,
            output_format=output_format,
            type=type,
            description=description,
            label_ordinality_by_user_label=label_ordinality_by_user_label,
            metadata=metadata,
            model_name=model_name,
            raw_label_by_user_label=raw_label_by_user_label,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
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
