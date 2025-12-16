from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.list_integrations_response_custom_inference_headers import (
        ListIntegrationsResponseCustomInferenceHeaders,  # noqa: F401
    )
    from ..models.list_integrations_response_custom_inference_transform_spec import (
        ListIntegrationsResponseCustomInferenceTransformSpec,  # noqa: F401
    )
    from ..models.list_integrations_response_integrations import (
        ListIntegrationsResponseIntegrations,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ListIntegrationsResponse")


@attrs.define
class ListIntegrationsResponse:
    """
    Attributes:
        custom_inference_headers (ListIntegrationsResponseCustomInferenceHeaders):
        custom_inference_transform_spec (ListIntegrationsResponseCustomInferenceTransformSpec):
        integrations (ListIntegrationsResponseIntegrations):
    """

    custom_inference_headers: "ListIntegrationsResponseCustomInferenceHeaders"
    custom_inference_transform_spec: (
        "ListIntegrationsResponseCustomInferenceTransformSpec"
    )
    integrations: "ListIntegrationsResponseIntegrations"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.list_integrations_response_custom_inference_headers import (
            ListIntegrationsResponseCustomInferenceHeaders,  # noqa: F401
        )
        from ..models.list_integrations_response_custom_inference_transform_spec import (
            ListIntegrationsResponseCustomInferenceTransformSpec,  # noqa: F401
        )
        from ..models.list_integrations_response_integrations import (
            ListIntegrationsResponseIntegrations,  # noqa: F401
        )
        # fmt: on
        custom_inference_headers = self.custom_inference_headers.to_dict()
        custom_inference_transform_spec = self.custom_inference_transform_spec.to_dict()
        integrations = self.integrations.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "custom_inference_headers": custom_inference_headers,
                "custom_inference_transform_spec": custom_inference_transform_spec,
                "integrations": integrations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.list_integrations_response_custom_inference_headers import (
            ListIntegrationsResponseCustomInferenceHeaders,  # noqa: F401
        )
        from ..models.list_integrations_response_custom_inference_transform_spec import (
            ListIntegrationsResponseCustomInferenceTransformSpec,  # noqa: F401
        )
        from ..models.list_integrations_response_integrations import (
            ListIntegrationsResponseIntegrations,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        custom_inference_headers = (
            ListIntegrationsResponseCustomInferenceHeaders.from_dict(
                d.pop("custom_inference_headers")
            )
        )

        custom_inference_transform_spec = (
            ListIntegrationsResponseCustomInferenceTransformSpec.from_dict(
                d.pop("custom_inference_transform_spec")
            )
        )

        integrations = ListIntegrationsResponseIntegrations.from_dict(
            d.pop("integrations")
        )

        obj = cls(
            custom_inference_headers=custom_inference_headers,
            custom_inference_transform_spec=custom_inference_transform_spec,
            integrations=integrations,
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
