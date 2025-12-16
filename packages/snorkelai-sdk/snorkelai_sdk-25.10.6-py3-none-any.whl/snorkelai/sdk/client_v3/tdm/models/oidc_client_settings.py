from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

T = TypeVar("T", bound="OidcClientSettings")


@attrs.define
class OidcClientSettings:
    """
    Attributes:
        authorization_endpoint (Union[Unset, str]):
        client_id (Union[Unset, str]):
        client_secret (Union[Unset, str]):
        issuer (Union[Unset, str]):
        jwks_uri (Union[Unset, str]):
        redirect_uris (Union[Unset, List[str]]):
        resource_id (Union[Unset, str]):
        token_endpoint (Union[Unset, str]):
        userinfo_endpoint (Union[Unset, str]):
        userinfo_handler (Union[Unset, str]):
        userinfo_uid (Union[Unset, str]):
    """

    authorization_endpoint: Union[Unset, str] = UNSET
    client_id: Union[Unset, str] = UNSET
    client_secret: Union[Unset, str] = UNSET
    issuer: Union[Unset, str] = UNSET
    jwks_uri: Union[Unset, str] = UNSET
    redirect_uris: Union[Unset, List[str]] = UNSET
    resource_id: Union[Unset, str] = UNSET
    token_endpoint: Union[Unset, str] = UNSET
    userinfo_endpoint: Union[Unset, str] = UNSET
    userinfo_handler: Union[Unset, str] = UNSET
    userinfo_uid: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        authorization_endpoint = self.authorization_endpoint
        client_id = self.client_id
        client_secret = self.client_secret
        issuer = self.issuer
        jwks_uri = self.jwks_uri
        redirect_uris: Union[Unset, List[str]] = UNSET
        if not isinstance(self.redirect_uris, Unset):
            redirect_uris = self.redirect_uris

        resource_id = self.resource_id
        token_endpoint = self.token_endpoint
        userinfo_endpoint = self.userinfo_endpoint
        userinfo_handler = self.userinfo_handler
        userinfo_uid = self.userinfo_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authorization_endpoint is not UNSET:
            field_dict["authorization_endpoint"] = authorization_endpoint
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret
        if issuer is not UNSET:
            field_dict["issuer"] = issuer
        if jwks_uri is not UNSET:
            field_dict["jwks_uri"] = jwks_uri
        if redirect_uris is not UNSET:
            field_dict["redirect_uris"] = redirect_uris
        if resource_id is not UNSET:
            field_dict["resource_id"] = resource_id
        if token_endpoint is not UNSET:
            field_dict["token_endpoint"] = token_endpoint
        if userinfo_endpoint is not UNSET:
            field_dict["userinfo_endpoint"] = userinfo_endpoint
        if userinfo_handler is not UNSET:
            field_dict["userinfo_handler"] = userinfo_handler
        if userinfo_uid is not UNSET:
            field_dict["userinfo_uid"] = userinfo_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _authorization_endpoint = d.pop("authorization_endpoint", UNSET)
        authorization_endpoint = (
            UNSET if _authorization_endpoint is None else _authorization_endpoint
        )

        _client_id = d.pop("client_id", UNSET)
        client_id = UNSET if _client_id is None else _client_id

        _client_secret = d.pop("client_secret", UNSET)
        client_secret = UNSET if _client_secret is None else _client_secret

        _issuer = d.pop("issuer", UNSET)
        issuer = UNSET if _issuer is None else _issuer

        _jwks_uri = d.pop("jwks_uri", UNSET)
        jwks_uri = UNSET if _jwks_uri is None else _jwks_uri

        _redirect_uris = d.pop("redirect_uris", UNSET)
        redirect_uris = cast(
            List[str], UNSET if _redirect_uris is None else _redirect_uris
        )

        _resource_id = d.pop("resource_id", UNSET)
        resource_id = UNSET if _resource_id is None else _resource_id

        _token_endpoint = d.pop("token_endpoint", UNSET)
        token_endpoint = UNSET if _token_endpoint is None else _token_endpoint

        _userinfo_endpoint = d.pop("userinfo_endpoint", UNSET)
        userinfo_endpoint = UNSET if _userinfo_endpoint is None else _userinfo_endpoint

        _userinfo_handler = d.pop("userinfo_handler", UNSET)
        userinfo_handler = UNSET if _userinfo_handler is None else _userinfo_handler

        _userinfo_uid = d.pop("userinfo_uid", UNSET)
        userinfo_uid = UNSET if _userinfo_uid is None else _userinfo_uid

        obj = cls(
            authorization_endpoint=authorization_endpoint,
            client_id=client_id,
            client_secret=client_secret,
            issuer=issuer,
            jwks_uri=jwks_uri,
            redirect_uris=redirect_uris,
            resource_id=resource_id,
            token_endpoint=token_endpoint,
            userinfo_endpoint=userinfo_endpoint,
            userinfo_handler=userinfo_handler,
            userinfo_uid=userinfo_uid,
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
