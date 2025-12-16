# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import OidcCallbackResponseData


@overload
def callback_oidc_sso_oidc_callback_get(raw: Literal[True]) -> requests.Response: ...


@overload
def callback_oidc_sso_oidc_callback_get(
    raw: Literal[False] = False,
) -> OidcCallbackResponseData: ...


def callback_oidc_sso_oidc_callback_get(
    raw: bool = False,
) -> OidcCallbackResponseData | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/oidc/callback",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> OidcCallbackResponseData:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as OidcCallbackResponseData
        response_200 = OidcCallbackResponseData.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import AuthSettings


@overload
def get_auth_settings_authentication_settings_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_auth_settings_authentication_settings_get(
    raw: Literal[False] = False,
) -> AuthSettings: ...


def get_auth_settings_authentication_settings_get(
    raw: bool = False,
) -> AuthSettings | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/authentication/settings",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AuthSettings:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AuthSettings
        response_200 = AuthSettings.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import OidcClientSettings


@overload
def get_oidc_settings_sso_settings_oidc_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_oidc_settings_sso_settings_oidc_get(
    raw: Literal[False] = False,
) -> OidcClientSettings: ...


def get_oidc_settings_sso_settings_oidc_get(
    raw: bool = False,
) -> OidcClientSettings | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings/oidc",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> OidcClientSettings:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as OidcClientSettings
        response_200 = OidcClientSettings.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import SamlSettingsResponse


@overload
def get_saml_settings_sso_settings_saml_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_saml_settings_sso_settings_saml_get(
    raw: Literal[False] = False,
) -> SamlSettingsResponse: ...


def get_saml_settings_sso_settings_saml_get(
    raw: bool = False,
) -> SamlSettingsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings/saml",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> SamlSettingsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SamlSettingsResponse
        response_200 = SamlSettingsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import SsoSettings


@overload
def get_sso_settings_sso_settings_get(raw: Literal[True]) -> requests.Response: ...


@overload
def get_sso_settings_sso_settings_get(raw: Literal[False] = False) -> SsoSettings: ...


def get_sso_settings_sso_settings_get(
    raw: bool = False,
) -> SsoSettings | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> SsoSettings:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SsoSettings
        response_200 = SsoSettings.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import cast, overload

import requests
from typing_extensions import Literal


@overload
def has_oidc_envs_set_sso_oidc_use_env_get(raw: Literal[True]) -> requests.Response: ...


@overload
def has_oidc_envs_set_sso_oidc_use_env_get(raw: Literal[False] = False) -> bool: ...


def has_oidc_envs_set_sso_oidc_use_env_get(
    raw: bool = False,
) -> bool | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/oidc-use-env",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> bool:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as bool
        # Direct parsing for bool
        return cast(bool, response)

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import AdmissionRoles


@overload
def list_admission_roles_sso_admission_roles_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_admission_roles_sso_admission_roles_get(
    raw: Literal[False] = False,
) -> AdmissionRoles: ...


def list_admission_roles_sso_admission_roles_get(
    raw: bool = False,
) -> AdmissionRoles | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/admission-roles",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AdmissionRoles:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AdmissionRoles
        response_200 = AdmissionRoles.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import SamlResponseData


def saml_login_callback_sso_saml_acs_post() -> SamlResponseData:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/saml/acs",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SamlResponseData:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SamlResponseData
        response_200 = SamlResponseData.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import SamlIdpSettings


def saml_settings_sso_settings_saml_post(
    *,
    body: SamlIdpSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings/saml",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import AdmissionRoles


def set_admission_roles_sso_admission_roles_post(
    *,
    body: AdmissionRoles,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/admission-roles",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import AuthSettings


def set_auth_settings_authentication_settings_post(
    *,
    body: AuthSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/authentication/settings",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import OidcClientSettings


def set_oidc_settings_sso_settings_oidc_post(
    *,
    body: OidcClientSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings/oidc",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any

from ..models import SsoSettings


def sso_settings_sso_settings_post(
    *,
    body: SsoSettings,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/settings",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import OidcStartSso
from ..types import UNSET, Unset


@overload
def start_oidc_sso_oidc_start_get(
    *,
    next_url: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def start_oidc_sso_oidc_start_get(
    *,
    next_url: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> OidcStartSso: ...


def start_oidc_sso_oidc_start_get(
    *,
    next_url: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> OidcStartSso | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["next_url"] = next_url

    params["invite_link"] = invite_link

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/oidc/start",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> OidcStartSso:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as OidcStartSso
        response_200 = OidcStartSso.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import SamlStartSso
from ..types import UNSET, Unset


@overload
def start_saml_auth_flow_sso_saml_start_get(
    *,
    return_to: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def start_saml_auth_flow_sso_saml_start_get(
    *,
    return_to: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> SamlStartSso: ...


def start_saml_auth_flow_sso_saml_start_get(
    *,
    return_to: Union[Unset, str] = UNSET,
    invite_link: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> SamlStartSso | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["return_to"] = return_to

    params["invite_link"] = invite_link

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/sso/saml/start",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> SamlStartSso:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SamlStartSso
        response_200 = SamlStartSso.from_dict(response)

        return response_200

    return _parse_response(response)
