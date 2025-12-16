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
    from ..models.create_criteria_payload_label_ordinality_by_user_label import (
        CreateCriteriaPayloadLabelOrdinalityByUserLabel,  # noqa: F401
    )
    from ..models.create_criteria_payload_raw_label_by_user_label import (
        CreateCriteriaPayloadRawLabelByUserLabel,  # noqa: F401
    )
    from ..models.create_new_prompt_version import CreateNewPromptVersion  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreateCriteriaPayload")


@attrs.define
class CreateCriteriaPayload:
    """
    Attributes:
        benchmark_uid (int):
        dataset_uid (int):
        name (str):
        description (Union[Unset, str]):
        filter_config (Union[Unset, str]):
        label_ordinality_by_user_label (Union[Unset, CreateCriteriaPayloadLabelOrdinalityByUserLabel]):
        prompt_configuration (Union[Unset, CreateNewPromptVersion]):
        raw_label_by_user_label (Union[Unset, CreateCriteriaPayloadRawLabelByUserLabel]):
        requires_rationale (Union[Unset, bool]):  Default: False.
    """

    benchmark_uid: int
    dataset_uid: int
    name: str
    description: Union[Unset, str] = UNSET
    filter_config: Union[Unset, str] = UNSET
    label_ordinality_by_user_label: Union[
        Unset, "CreateCriteriaPayloadLabelOrdinalityByUserLabel"
    ] = UNSET
    prompt_configuration: Union[Unset, "CreateNewPromptVersion"] = UNSET
    raw_label_by_user_label: Union[
        Unset, "CreateCriteriaPayloadRawLabelByUserLabel"
    ] = UNSET
    requires_rationale: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_criteria_payload_label_ordinality_by_user_label import (
            CreateCriteriaPayloadLabelOrdinalityByUserLabel,  # noqa: F401
        )
        from ..models.create_criteria_payload_raw_label_by_user_label import (
            CreateCriteriaPayloadRawLabelByUserLabel,  # noqa: F401
        )
        from ..models.create_new_prompt_version import (
            CreateNewPromptVersion,  # noqa: F401
        )
        # fmt: on
        benchmark_uid = self.benchmark_uid
        dataset_uid = self.dataset_uid
        name = self.name
        description = self.description
        filter_config = self.filter_config
        label_ordinality_by_user_label: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_ordinality_by_user_label, Unset):
            label_ordinality_by_user_label = (
                self.label_ordinality_by_user_label.to_dict()
            )
        prompt_configuration: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.prompt_configuration, Unset):
            prompt_configuration = self.prompt_configuration.to_dict()
        raw_label_by_user_label: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.raw_label_by_user_label, Unset):
            raw_label_by_user_label = self.raw_label_by_user_label.to_dict()
        requires_rationale = self.requires_rationale

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_uid": benchmark_uid,
                "dataset_uid": dataset_uid,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if filter_config is not UNSET:
            field_dict["filter_config"] = filter_config
        if label_ordinality_by_user_label is not UNSET:
            field_dict["label_ordinality_by_user_label"] = (
                label_ordinality_by_user_label
            )
        if prompt_configuration is not UNSET:
            field_dict["prompt_configuration"] = prompt_configuration
        if raw_label_by_user_label is not UNSET:
            field_dict["raw_label_by_user_label"] = raw_label_by_user_label
        if requires_rationale is not UNSET:
            field_dict["requires_rationale"] = requires_rationale

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_criteria_payload_label_ordinality_by_user_label import (
            CreateCriteriaPayloadLabelOrdinalityByUserLabel,  # noqa: F401
        )
        from ..models.create_criteria_payload_raw_label_by_user_label import (
            CreateCriteriaPayloadRawLabelByUserLabel,  # noqa: F401
        )
        from ..models.create_new_prompt_version import (
            CreateNewPromptVersion,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        benchmark_uid = d.pop("benchmark_uid")

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _filter_config = d.pop("filter_config", UNSET)
        filter_config = UNSET if _filter_config is None else _filter_config

        _label_ordinality_by_user_label = d.pop("label_ordinality_by_user_label", UNSET)
        _label_ordinality_by_user_label = (
            UNSET
            if _label_ordinality_by_user_label is None
            else _label_ordinality_by_user_label
        )
        label_ordinality_by_user_label: Union[
            Unset, CreateCriteriaPayloadLabelOrdinalityByUserLabel
        ]
        if isinstance(_label_ordinality_by_user_label, Unset):
            label_ordinality_by_user_label = UNSET
        else:
            label_ordinality_by_user_label = (
                CreateCriteriaPayloadLabelOrdinalityByUserLabel.from_dict(
                    _label_ordinality_by_user_label
                )
            )

        _prompt_configuration = d.pop("prompt_configuration", UNSET)
        _prompt_configuration = (
            UNSET if _prompt_configuration is None else _prompt_configuration
        )
        prompt_configuration: Union[Unset, CreateNewPromptVersion]
        if isinstance(_prompt_configuration, Unset):
            prompt_configuration = UNSET
        else:
            prompt_configuration = CreateNewPromptVersion.from_dict(
                _prompt_configuration
            )

        _raw_label_by_user_label = d.pop("raw_label_by_user_label", UNSET)
        _raw_label_by_user_label = (
            UNSET if _raw_label_by_user_label is None else _raw_label_by_user_label
        )
        raw_label_by_user_label: Union[Unset, CreateCriteriaPayloadRawLabelByUserLabel]
        if isinstance(_raw_label_by_user_label, Unset):
            raw_label_by_user_label = UNSET
        else:
            raw_label_by_user_label = (
                CreateCriteriaPayloadRawLabelByUserLabel.from_dict(
                    _raw_label_by_user_label
                )
            )

        _requires_rationale = d.pop("requires_rationale", UNSET)
        requires_rationale = (
            UNSET if _requires_rationale is None else _requires_rationale
        )

        obj = cls(
            benchmark_uid=benchmark_uid,
            dataset_uid=dataset_uid,
            name=name,
            description=description,
            filter_config=filter_config,
            label_ordinality_by_user_label=label_ordinality_by_user_label,
            prompt_configuration=prompt_configuration,
            raw_label_by_user_label=raw_label_by_user_label,
            requires_rationale=requires_rationale,
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
