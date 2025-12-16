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

T = TypeVar("T", bound="BedrockSecretsConfig")


@attrs.define
class BedrockSecretsConfig:
    """
    Attributes:
        provider (Literal['bedrock']):
        awsbedrockaccess_key_id (Union[Unset, str]):
        awsbedrockexecution_role (Union[Unset, str]):
        awsbedrockregion (Union[Unset, str]):
        awsbedrocksecret_access_key (Union[Unset, str]):
    """

    provider: Literal["bedrock"]
    awsbedrockaccess_key_id: Union[Unset, str] = UNSET
    awsbedrockexecution_role: Union[Unset, str] = UNSET
    awsbedrockregion: Union[Unset, str] = UNSET
    awsbedrocksecret_access_key: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provider = self.provider
        awsbedrockaccess_key_id = self.awsbedrockaccess_key_id
        awsbedrockexecution_role = self.awsbedrockexecution_role
        awsbedrockregion = self.awsbedrockregion
        awsbedrocksecret_access_key = self.awsbedrocksecret_access_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
            }
        )
        if awsbedrockaccess_key_id is not UNSET:
            field_dict["aws::bedrock::access_key_id"] = awsbedrockaccess_key_id
        if awsbedrockexecution_role is not UNSET:
            field_dict["aws::bedrock::execution_role"] = awsbedrockexecution_role
        if awsbedrockregion is not UNSET:
            field_dict["aws::bedrock::region"] = awsbedrockregion
        if awsbedrocksecret_access_key is not UNSET:
            field_dict["aws::bedrock::secret_access_key"] = awsbedrocksecret_access_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provider = d.pop("provider")

        _awsbedrockaccess_key_id = d.pop("aws::bedrock::access_key_id", UNSET)
        awsbedrockaccess_key_id = (
            UNSET if _awsbedrockaccess_key_id is None else _awsbedrockaccess_key_id
        )

        _awsbedrockexecution_role = d.pop("aws::bedrock::execution_role", UNSET)
        awsbedrockexecution_role = (
            UNSET if _awsbedrockexecution_role is None else _awsbedrockexecution_role
        )

        _awsbedrockregion = d.pop("aws::bedrock::region", UNSET)
        awsbedrockregion = UNSET if _awsbedrockregion is None else _awsbedrockregion

        _awsbedrocksecret_access_key = d.pop("aws::bedrock::secret_access_key", UNSET)
        awsbedrocksecret_access_key = (
            UNSET
            if _awsbedrocksecret_access_key is None
            else _awsbedrocksecret_access_key
        )

        obj = cls(
            provider=provider,
            awsbedrockaccess_key_id=awsbedrockaccess_key_id,
            awsbedrockexecution_role=awsbedrockexecution_role,
            awsbedrockregion=awsbedrockregion,
            awsbedrocksecret_access_key=awsbedrocksecret_access_key,
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
