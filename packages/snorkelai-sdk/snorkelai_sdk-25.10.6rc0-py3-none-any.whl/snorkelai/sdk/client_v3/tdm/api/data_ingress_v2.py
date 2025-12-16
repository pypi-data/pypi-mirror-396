# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    AnalyzeDatasourcesRequest,
    AnalyzeDatasourcesResponse,
)


def analyze_datasources_v2_datasets__dataset_uid__datasources_actions_analyze_post(
    dataset_uid: int,
    *,
    body: AnalyzeDatasourcesRequest,
) -> AnalyzeDatasourcesResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasets/{dataset_uid}/datasources/actions/analyze",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> AnalyzeDatasourcesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AnalyzeDatasourcesResponse
        response_200 = AnalyzeDatasourcesResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    DeleteDatasourceRequest,
    DeleteDatasourceResponse,
)


def delete_datasource_v2_datasets__dataset_uid__datasources__datasource_uid__delete(
    dataset_uid: int,
    datasource_uid: int,
    *,
    body: DeleteDatasourceRequest,
) -> DeleteDatasourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasets/{dataset_uid}/datasources/{datasource_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DeleteDatasourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DeleteDatasourceResponse
        response_202 = DeleteDatasourceResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import DatasourceDetailResponse


@overload
def get_datasource_v2_datasources__datasource_uid__get(
    datasource_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_datasource_v2_datasources__datasource_uid__get(
    datasource_uid: int, raw: Literal[False] = False
) -> DatasourceDetailResponse: ...


def get_datasource_v2_datasources__datasource_uid__get(
    datasource_uid: int, raw: bool = False
) -> DatasourceDetailResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasources/{datasource_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasourceDetailResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasourceDetailResponse
        response_200 = DatasourceDetailResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    IngestDatasourcesResponse,
    UnifiedIngestDatasourcesRequest,
)
from ..types import UNSET


def ingest_datasources_v2_datasources_actions_ingest_post(
    *,
    body: UnifiedIngestDatasourcesRequest,
    workspace_uid: int,
) -> IngestDatasourcesResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v2/datasources/actions/ingest",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> IngestDatasourcesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as IngestDatasourcesResponse
        response_201 = IngestDatasourcesResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Union, overload

import requests
from typing_extensions import Literal

from ..models import DatasourceListResponse
from ..types import Unset


@overload
def list_datasources_v2_datasets__dataset_uid__datasources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_datasources_v2_datasets__dataset_uid__datasources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> DatasourceListResponse: ...


def list_datasources_v2_datasets__dataset_uid__datasources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> DatasourceListResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["datasource_name"] = datasource_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasets/{dataset_uid}/datasources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasourceListResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasourceListResponse
        response_200 = DatasourceListResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    PreviewDatasourceResponse,
    UnifiedPreviewRequest,
)


def preview_datasource_v2_datasources_actions_preview_post(
    *,
    body: UnifiedPreviewRequest,
) -> PreviewDatasourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/v2/datasources/actions/preview",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PreviewDatasourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PreviewDatasourceResponse
        response_200 = PreviewDatasourceResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    SplitByPercentageDatasourceIngestionRequest,
    SplitDatasourcesResponse,
)


def split_datasources_v2_datasets__dataset_uid__datasources_actions_split_post(
    dataset_uid: int,
    *,
    body: SplitByPercentageDatasourceIngestionRequest,
) -> SplitDatasourcesResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasets/{dataset_uid}/datasources/actions/split",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SplitDatasourcesResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SplitDatasourcesResponse
        response_201 = SplitDatasourcesResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import UpdateDatasourceRequest


def update_datasource_v2_datasources__datasource_uid__patch(
    datasource_uid: int,
    *,
    body: UpdateDatasourceRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/v2/datasources/{datasource_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.patch(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
