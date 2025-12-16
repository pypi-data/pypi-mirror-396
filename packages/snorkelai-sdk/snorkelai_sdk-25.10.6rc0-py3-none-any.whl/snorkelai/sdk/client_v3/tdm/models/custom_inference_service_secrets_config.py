from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.custom_inference_service_secrets_config_custom_inference_optional_headers import (
        CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders,  # noqa: F401
    )
    from ..models.custom_inference_service_secrets_config_custom_inference_transform_spec import (
        CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CustomInferenceServiceSecretsConfig")


@attrs.define
class CustomInferenceServiceSecretsConfig:
    """
    Attributes:
        provider (Literal['custom_inference_service']):
        custom_inference_api_key (Union[Unset, str]):
        custom_inference_optional_headers (Union[Unset,
            CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders]):
        custom_inference_transform_spec (Union[Unset, CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec]):
    """

    provider: Literal["custom_inference_service"]
    custom_inference_api_key: Union[Unset, str] = UNSET
    custom_inference_optional_headers: Union[
        Unset, "CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders"
    ] = UNSET
    custom_inference_transform_spec: Union[
        Unset, "CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec"
    ] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.custom_inference_service_secrets_config_custom_inference_optional_headers import (
            CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders,  # noqa: F401
        )
        from ..models.custom_inference_service_secrets_config_custom_inference_transform_spec import (
            CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec,  # noqa: F401
        )
        # fmt: on
        provider = self.provider
        custom_inference_api_key = self.custom_inference_api_key
        custom_inference_optional_headers: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.custom_inference_optional_headers, Unset):
            custom_inference_optional_headers = (
                self.custom_inference_optional_headers.to_dict()
            )
        custom_inference_transform_spec: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.custom_inference_transform_spec, Unset):
            custom_inference_transform_spec = (
                self.custom_inference_transform_spec.to_dict()
            )

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if custom_inference_api_key is not UNSET:
            field_dict["custom_inference_api_key"] = custom_inference_api_key
        if custom_inference_optional_headers is not UNSET:
            field_dict["custom_inference_optional_headers"] = (
                custom_inference_optional_headers
            )
        if custom_inference_transform_spec is not UNSET:
            field_dict["custom_inference_transform_spec"] = (
                custom_inference_transform_spec
            )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.custom_inference_service_secrets_config_custom_inference_optional_headers import (
            CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders,  # noqa: F401
        )
        from ..models.custom_inference_service_secrets_config_custom_inference_transform_spec import (
            CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        provider = d.pop("provider")

        _custom_inference_api_key = d.pop("custom_inference_api_key", UNSET)
        custom_inference_api_key = (
            UNSET if _custom_inference_api_key is None else _custom_inference_api_key
        )

        _custom_inference_optional_headers = d.pop(
            "custom_inference_optional_headers", UNSET
        )
        _custom_inference_optional_headers = (
            UNSET
            if _custom_inference_optional_headers is None
            else _custom_inference_optional_headers
        )
        custom_inference_optional_headers: Union[
            Unset, CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders
        ]
        if isinstance(_custom_inference_optional_headers, Unset):
            custom_inference_optional_headers = UNSET
        else:
            custom_inference_optional_headers = CustomInferenceServiceSecretsConfigCustomInferenceOptionalHeaders.from_dict(
                _custom_inference_optional_headers
            )

        _custom_inference_transform_spec = d.pop(
            "custom_inference_transform_spec", UNSET
        )
        _custom_inference_transform_spec = (
            UNSET
            if _custom_inference_transform_spec is None
            else _custom_inference_transform_spec
        )
        custom_inference_transform_spec: Union[
            Unset, CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec
        ]
        if isinstance(_custom_inference_transform_spec, Unset):
            custom_inference_transform_spec = UNSET
        else:
            custom_inference_transform_spec = CustomInferenceServiceSecretsConfigCustomInferenceTransformSpec.from_dict(
                _custom_inference_transform_spec
            )

        obj = cls(
            provider=provider,
            custom_inference_api_key=custom_inference_api_key,
            custom_inference_optional_headers=custom_inference_optional_headers,
            custom_inference_transform_spec=custom_inference_transform_spec,
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
