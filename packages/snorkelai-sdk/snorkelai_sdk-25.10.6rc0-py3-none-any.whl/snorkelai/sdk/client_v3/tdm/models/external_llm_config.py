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

from ..models.external_llm_provider import ExternalLLMProvider
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.external_llm_config_config import (
        ExternalLLMConfigConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ExternalLLMConfig")


@attrs.define
class ExternalLLMConfig:
    """
    Attributes:
        model_name (str):
        model_provider (ExternalLLMProvider):
        workspace_uid (int):
        config (Union[Unset, ExternalLLMConfigConfig]):
        created_at (Union[Unset, datetime.datetime]):
        external_llm_config_uid (Union[Unset, int]):
    """

    model_name: str
    model_provider: ExternalLLMProvider
    workspace_uid: int
    config: Union[Unset, "ExternalLLMConfigConfig"] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    external_llm_config_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.external_llm_config_config import (
            ExternalLLMConfigConfig,  # noqa: F401
        )
        # fmt: on
        model_name = self.model_name
        model_provider = self.model_provider.value
        workspace_uid = self.workspace_uid
        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        external_llm_config_uid = self.external_llm_config_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_name": model_name,
                "model_provider": model_provider,
                "workspace_uid": workspace_uid,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if external_llm_config_uid is not UNSET:
            field_dict["external_llm_config_uid"] = external_llm_config_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.external_llm_config_config import (
            ExternalLLMConfigConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        model_name = d.pop("model_name")

        model_provider = ExternalLLMProvider(d.pop("model_provider"))

        workspace_uid = d.pop("workspace_uid")

        _config = d.pop("config", UNSET)
        _config = UNSET if _config is None else _config
        config: Union[Unset, ExternalLLMConfigConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = ExternalLLMConfigConfig.from_dict(_config)

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _external_llm_config_uid = d.pop("external_llm_config_uid", UNSET)
        external_llm_config_uid = (
            UNSET if _external_llm_config_uid is None else _external_llm_config_uid
        )

        obj = cls(
            model_name=model_name,
            model_provider=model_provider,
            workspace_uid=workspace_uid,
            config=config,
            created_at=created_at,
            external_llm_config_uid=external_llm_config_uid,
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
