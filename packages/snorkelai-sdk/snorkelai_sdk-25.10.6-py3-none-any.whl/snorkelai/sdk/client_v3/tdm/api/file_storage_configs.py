# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import FileStorageConfig, FileStorageConfigCreate


def create_file_storage_config_file_storage_configs_post(
    *,
    body: FileStorageConfigCreate,
) -> FileStorageConfig:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/file-storage-configs",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> FileStorageConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as FileStorageConfig
        response_200 = FileStorageConfig.from_dict(response)

        return response_200

    return _parse_response(response)


def delete_file_storage_config_file_storage_configs__file_storage_config_uid__delete(
    file_storage_config_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/file-storage-configs/{file_storage_config_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any, overload

import requests
from typing_extensions import Literal

from ..models import FileStorageConfig


@overload
def get_file_storage_config_file_storage_configs__file_storage_config_uid__get(
    file_storage_config_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_file_storage_config_file_storage_configs__file_storage_config_uid__get(
    file_storage_config_uid: int, raw: Literal[False] = False
) -> FileStorageConfig: ...


def get_file_storage_config_file_storage_configs__file_storage_config_uid__get(
    file_storage_config_uid: int, raw: bool = False
) -> FileStorageConfig | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/file-storage-configs/{file_storage_config_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> FileStorageConfig:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as FileStorageConfig
        response_200 = FileStorageConfig.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, List, overload

import requests
from typing_extensions import Literal

from ..models import FileStorageConfig


@overload
def list_file_storage_configs_file_storage_configs_get(
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_file_storage_configs_file_storage_configs_get(
    raw: Literal[False] = False,
) -> List["FileStorageConfig"]: ...


def list_file_storage_configs_file_storage_configs_get(
    raw: bool = False,
) -> List["FileStorageConfig"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/file-storage-configs",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["FileStorageConfig"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['FileStorageConfig']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = FileStorageConfig.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import SetDefaultFileStorageConfigParams


def set_default_file_storage_config_file_storage_configs_set_default_put(
    *,
    body: SetDefaultFileStorageConfigParams,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/file-storage-configs/set-default",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
