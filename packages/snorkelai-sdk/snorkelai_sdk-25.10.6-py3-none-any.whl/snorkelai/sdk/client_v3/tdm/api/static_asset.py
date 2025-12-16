# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import StaticAssetFileMetadata
from ..types import UNSET, Unset


@overload
def list_asset_folder_files_static_asset_list_asset_folder_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    folder_type: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_asset_folder_files_static_asset_list_asset_folder_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    folder_type: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: Literal[False] = False,
) -> List["StaticAssetFileMetadata"]: ...


def list_asset_folder_files_static_asset_list_asset_folder_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    folder_type: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: bool = False,
) -> List["StaticAssetFileMetadata"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["folder_name"] = folder_name

    params["folder_type"] = folder_type

    params["only_tabular"] = only_tabular

    params["page"] = page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset/list-asset-folder-files",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["StaticAssetFileMetadata"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['StaticAssetFileMetadata']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = StaticAssetFileMetadata.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import (
    ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet,
)
from ..types import Unset


@overload
def list_asset_folder_names_static_asset_list_asset_folder_names_get(
    *, workspace_uid: int, only_tabular: Union[Unset, bool] = False, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_asset_folder_names_static_asset_list_asset_folder_names_get(
    *,
    workspace_uid: int,
    only_tabular: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet: ...


def list_asset_folder_names_static_asset_list_asset_folder_names_get(
    *, workspace_uid: int, only_tabular: Union[Unset, bool] = False, raw: bool = False
) -> (
    ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["only_tabular"] = only_tabular

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset/list-asset-folder-names",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(
        response: Any,
    ) -> ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet
        response_200 = ListAssetFolderNamesStaticAssetListAssetFolderNamesGetResponseListAssetFolderNamesStaticAssetListAssetFolderNamesGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)


from typing import List, Union, overload

import requests
from typing_extensions import Literal

from ..types import Unset


@overload
def search_files_static_asset_search_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    search_query: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def search_files_static_asset_search_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    search_query: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: Literal[False] = False,
) -> List["StaticAssetFileMetadata"]: ...


def search_files_static_asset_search_files_get(
    *,
    workspace_uid: int,
    folder_name: str,
    search_query: str,
    only_tabular: Union[Unset, bool] = False,
    page: Union[Unset, int] = 1,
    raw: bool = False,
) -> List["StaticAssetFileMetadata"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["folder_name"] = folder_name

    params["search_query"] = search_query

    params["only_tabular"] = only_tabular

    params["page"] = page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset/search-files",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["StaticAssetFileMetadata"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['StaticAssetFileMetadata']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = StaticAssetFileMetadata.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Union

from ..models import (
    AssetUploadType,
    BodyUploadLocalStaticAssetUploadLocalFilesPost,
    UploadLocalFileResponseModel,
)
from ..types import Unset


def upload_local_static_asset_upload_local_files_post(
    *,
    body: BodyUploadLocalStaticAssetUploadLocalFilesPost,
    workspace_uid: int,
    file_type: AssetUploadType,
    overwrite_existing: Union[Unset, bool] = True,
) -> UploadLocalFileResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    json_file_type = file_type.value
    params["file_type"] = json_file_type

    params["overwrite_existing"] = overwrite_existing

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset/upload-local-files",
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UploadLocalFileResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UploadLocalFileResponseModel
        response_201 = UploadLocalFileResponseModel.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import AsyncJobResponse, UploadRemoteObjectsParams


def upload_remote_static_asset_upload_remote_files_post(
    *,
    body: UploadRemoteObjectsParams,
    workspace_uid: int,
) -> AsyncJobResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/static-asset/upload-remote-files",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AsyncJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AsyncJobResponse
        response_201 = AsyncJobResponse.from_dict(response)

        return response_201

    return _parse_response(response)
