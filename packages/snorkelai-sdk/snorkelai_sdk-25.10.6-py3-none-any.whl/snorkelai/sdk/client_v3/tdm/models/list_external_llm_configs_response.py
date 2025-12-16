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
    from ..models.external_llm_config import ExternalLLMConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ListExternalLLMConfigsResponse")


@attrs.define
class ListExternalLLMConfigsResponse:
    """
    Attributes:
        external_llm_configs (List['ExternalLLMConfig']):
    """

    external_llm_configs: List["ExternalLLMConfig"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.external_llm_config import ExternalLLMConfig  # noqa: F401
        # fmt: on
        external_llm_configs = []
        for external_llm_configs_item_data in self.external_llm_configs:
            external_llm_configs_item = external_llm_configs_item_data.to_dict()
            external_llm_configs.append(external_llm_configs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "external_llm_configs": external_llm_configs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.external_llm_config import ExternalLLMConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        external_llm_configs = []
        _external_llm_configs = d.pop("external_llm_configs")
        for external_llm_configs_item_data in _external_llm_configs:
            external_llm_configs_item = ExternalLLMConfig.from_dict(
                external_llm_configs_item_data
            )

            external_llm_configs.append(external_llm_configs_item)

        obj = cls(
            external_llm_configs=external_llm_configs,
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
