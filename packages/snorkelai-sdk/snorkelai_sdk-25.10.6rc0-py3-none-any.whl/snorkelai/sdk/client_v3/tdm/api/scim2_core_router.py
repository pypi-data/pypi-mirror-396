# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


def activate_scim_auth_scim_activate_post() -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/auth/scim/activate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any


def deactivate_scim_auth_scim_deactivate_post() -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/auth/scim/deactivate",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet,
    SCIMSchemaUrn,
)


@overload
def get_schema_scim_v2_Schemas__scim_schema_urn__get(
    scim_schema_urn: SCIMSchemaUrn, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_schema_scim_v2_Schemas__scim_schema_urn__get(
    scim_schema_urn: SCIMSchemaUrn, raw: Literal[False] = False
) -> (
    GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet
): ...


def get_schema_scim_v2_Schemas__scim_schema_urn__get(
    scim_schema_urn: SCIMSchemaUrn, raw: bool = False
) -> (
    GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/scim/v2/Schemas/{scim_schema_urn}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet
        response_200 = GetSchemaScimV2SchemasScimSchemaUrnGetResponseGetSchemaScimV2SchemasScimSchemaUrnGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet,
)


@overload
def get_service_provider_config_scim_v2_ServiceProviderConfig_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_service_provider_config_scim_v2_ServiceProviderConfig_get(
    raw: Literal[False] = False,
) -> GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet: ...


def get_service_provider_config_scim_v2_ServiceProviderConfig_get(
    raw: bool = False,
) -> (
    GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/ServiceProviderConfig",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet
        response_200 = GetServiceProviderConfigScimV2ServiceProviderConfigGetResponseGetServiceProviderConfigScimV2ServiceproviderconfigGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, cast, overload

import requests
from typing_extensions import Literal


@overload
def is_scim_enabled_auth_scim_enabled_get(raw: Literal[True]) -> requests.Response: ...


@overload
def is_scim_enabled_auth_scim_enabled_get(raw: Literal[False] = False) -> bool: ...


def is_scim_enabled_auth_scim_enabled_get(
    raw: bool = False,
) -> bool | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/auth/scim/enabled",
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


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet,
)


@overload
def list_resource_types_scim_v2_ResourceTypes_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_resource_types_scim_v2_ResourceTypes_get(
    raw: Literal[False] = False,
) -> ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet: ...


def list_resource_types_scim_v2_ResourceTypes_get(
    raw: bool = False,
) -> (
    ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/ResourceTypes",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet
        response_200 = ListResourceTypesScimV2ResourceTypesGetResponseListResourceTypesScimV2ResourcetypesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet


@overload
def list_schemas_scim_v2_Schemas_get(raw: Literal[True]) -> requests.Response: ...


@overload
def list_schemas_scim_v2_Schemas_get(
    raw: Literal[False] = False,
) -> ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet: ...


def list_schemas_scim_v2_Schemas_get(
    raw: bool = False,
) -> ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/scim/v2/Schemas",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet
        response_200 = (
            ListSchemasScimV2SchemasGetResponseListSchemasScimV2SchemasGet.from_dict(
                response
            )
        )

        return response_200

    return _parse_response(response)


from typing import Any


def regenerate_bearer_token_auth_scim_token_post() -> str:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/auth/scim/token",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> str:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as str
        # Direct parsing for str
        return cast(str, response)

    return _parse_response(response)
