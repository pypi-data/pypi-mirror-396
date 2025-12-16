from typing import (
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

T = TypeVar("T", bound="VertexAISecretsConfig")


@attrs.define
class VertexAISecretsConfig:
    """
    Attributes:
        provider (Literal['vertexai_lm']):
        vertexai_lm_credentials_json (Union[Unset, str]):
        vertexai_lm_location (Union[Unset, str]):
        vertexai_lm_project_id (Union[Unset, str]):
    """

    provider: Literal["vertexai_lm"]
    vertexai_lm_credentials_json: Union[Unset, str] = UNSET
    vertexai_lm_location: Union[Unset, str] = UNSET
    vertexai_lm_project_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider = self.provider
        vertexai_lm_credentials_json = self.vertexai_lm_credentials_json
        vertexai_lm_location = self.vertexai_lm_location
        vertexai_lm_project_id = self.vertexai_lm_project_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if vertexai_lm_credentials_json is not UNSET:
            field_dict["vertexai_lm_credentials_json"] = vertexai_lm_credentials_json
        if vertexai_lm_location is not UNSET:
            field_dict["vertexai_lm_location"] = vertexai_lm_location
        if vertexai_lm_project_id is not UNSET:
            field_dict["vertexai_lm_project_id"] = vertexai_lm_project_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provider = d.pop("provider")

        _vertexai_lm_credentials_json = d.pop("vertexai_lm_credentials_json", UNSET)
        vertexai_lm_credentials_json = (
            UNSET
            if _vertexai_lm_credentials_json is None
            else _vertexai_lm_credentials_json
        )

        _vertexai_lm_location = d.pop("vertexai_lm_location", UNSET)
        vertexai_lm_location = (
            UNSET if _vertexai_lm_location is None else _vertexai_lm_location
        )

        _vertexai_lm_project_id = d.pop("vertexai_lm_project_id", UNSET)
        vertexai_lm_project_id = (
            UNSET if _vertexai_lm_project_id is None else _vertexai_lm_project_id
        )

        obj = cls(
            provider=provider,
            vertexai_lm_credentials_json=vertexai_lm_credentials_json,
            vertexai_lm_location=vertexai_lm_location,
            vertexai_lm_project_id=vertexai_lm_project_id,
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
