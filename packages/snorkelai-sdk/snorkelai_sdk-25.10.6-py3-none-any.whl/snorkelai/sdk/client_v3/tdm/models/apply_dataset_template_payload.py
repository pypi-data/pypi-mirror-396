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
    from ..models.apply_dataset_template_payload_params import (
        ApplyDatasetTemplatePayloadParams,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ApplyDatasetTemplatePayload")


@attrs.define
class ApplyDatasetTemplatePayload:
    """
    Attributes:
        template_id (str):
        params (Union[Unset, ApplyDatasetTemplatePayloadParams]):
    """

    template_id: str
    params: Union[Unset, "ApplyDatasetTemplatePayloadParams"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.apply_dataset_template_payload_params import (
            ApplyDatasetTemplatePayloadParams,  # noqa: F401
        )
        # fmt: on
        template_id = self.template_id
        params: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template_id": template_id,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.apply_dataset_template_payload_params import (
            ApplyDatasetTemplatePayloadParams,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        template_id = d.pop("template_id")

        _params = d.pop("params", UNSET)
        _params = UNSET if _params is None else _params
        params: Union[Unset, ApplyDatasetTemplatePayloadParams]
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = ApplyDatasetTemplatePayloadParams.from_dict(_params)

        obj = cls(
            template_id=template_id,
            params=params,
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
