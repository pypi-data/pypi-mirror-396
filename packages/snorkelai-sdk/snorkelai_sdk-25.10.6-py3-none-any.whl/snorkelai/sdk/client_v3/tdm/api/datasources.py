# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    AnalyzeDataSourcesRequest,
    DatasourceAnalysisResponse,
)


def analyze_datasources_datasets__dataset_uid__analyze_data_sources_post(
    dataset_uid: int,
    *,
    body: AnalyzeDataSourcesRequest,
) -> List["DatasourceAnalysisResponse"]:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/analyze-data-sources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasourceAnalysisResponse"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasourceAnalysisResponse']
        response_201 = []
        _response_201 = response
        for response_201_item_data in _response_201:
            response_201_item = DatasourceAnalysisResponse.from_dict(
                response_201_item_data
            )

            response_201.append(response_201_item)

        return response_201

    return _parse_response(response)


from ..models import (
    DataSourceUniqueColumnValuesRequest,
    UniqueLabelsResponse,
)


def datasource_unique_values_datasets__dataset_uid__data_source_label_values_post(
    dataset_uid: int,
    *,
    body: DataSourceUniqueColumnValuesRequest,
) -> UniqueLabelsResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/data-source-label-values",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UniqueLabelsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UniqueLabelsResponse
        response_200 = UniqueLabelsResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    RemoveDatasourceRequest,
    RemoveDatasourceResponse,
)


def delete_datasource(
    dataset_uid: int,
    datasource_uid: int,
    *,
    body: RemoveDatasourceRequest,
) -> RemoveDatasourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/data-sources/{datasource_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.delete(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> RemoveDatasourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as RemoveDatasourceResponse
        response_202 = RemoveDatasourceResponse.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import AsyncJobResponse


@overload
def get_dataframe_data_sources__datasource_uid__dataframe_get(
    datasource_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_dataframe_data_sources__datasource_uid__dataframe_get(
    datasource_uid: int, raw: Literal[False] = False
) -> AsyncJobResponse: ...


def get_dataframe_data_sources__datasource_uid__dataframe_get(
    datasource_uid: int, raw: bool = False
) -> AsyncJobResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-sources/{datasource_uid}/dataframe",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AsyncJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AsyncJobResponse
        response_200 = AsyncJobResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import overload

import requests
from typing_extensions import Literal

from ..models import DatasourceMetadataBase


@overload
def get_datasource_metadata_data_sources__datasource_uid__metadata_get(
    datasource_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_datasource_metadata_data_sources__datasource_uid__metadata_get(
    datasource_uid: int, raw: Literal[False] = False
) -> DatasourceMetadataBase: ...


def get_datasource_metadata_data_sources__datasource_uid__metadata_get(
    datasource_uid: int, raw: bool = False
) -> DatasourceMetadataBase | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-sources/{datasource_uid}/metadata",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> DatasourceMetadataBase:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DatasourceMetadataBase
        response_200 = DatasourceMetadataBase.from_dict(response)

        return response_200

    return _parse_response(response)


from ..models import (
    IngestAllDataSourcesResponseModel,
    MultiDataSourcesIngestionRequest,
)


def ingest_all_datasources_datasets__dataset_uid__multi_data_sources_post(
    dataset_uid: int,
    *,
    body: MultiDataSourcesIngestionRequest,
) -> IngestAllDataSourcesResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/multi-data-sources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> IngestAllDataSourcesResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as IngestAllDataSourcesResponseModel
        response_201 = IngestAllDataSourcesResponseModel.from_dict(response)

        return response_201

    return _parse_response(response)


from ..models import SingleDataSourceIngestionRequest


def ingest_datasource_datasets__dataset_uid__data_sources_post(
    dataset_uid: int,
    *,
    body: SingleDataSourceIngestionRequest,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/data-sources",
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


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..models import DataSourceWithDatasetUid
from ..types import UNSET, Unset


@overload
def list_annotation_datasources_datasets__dataset_uid__annotation_data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_annotation_datasources_datasets__dataset_uid__annotation_data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> List["DataSourceWithDatasetUid"]: ...


def list_annotation_datasources_datasets__dataset_uid__annotation_data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> List["DataSourceWithDatasetUid"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["datasource_name"] = datasource_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/annotation-data-sources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DataSourceWithDatasetUid"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DataSourceWithDatasetUid']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DataSourceWithDatasetUid.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def list_dataset_datasources_datasets__dataset_uid__data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def list_dataset_datasources_datasets__dataset_uid__data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: Literal[False] = False,
) -> List["DataSourceWithDatasetUid"]: ...


def list_dataset_datasources_datasets__dataset_uid__data_sources_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    datasource_name: Union[Unset, str] = UNSET,
    raw: bool = False,
) -> List["DataSourceWithDatasetUid"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["datasource_name"] = datasource_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/data-sources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DataSourceWithDatasetUid"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DataSourceWithDatasetUid']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DataSourceWithDatasetUid.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any, List, Union, overload

import requests
from typing_extensions import Literal

from ..types import UNSET, Unset


@overload
def list_datasources_data_sources_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: Literal[True]
) -> requests.Response: ...


@overload
def list_datasources_data_sources_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: Literal[False] = False
) -> List["DataSourceWithDatasetUid"]: ...


def list_datasources_data_sources_get(
    *, workspace_uid: Union[Unset, int] = UNSET, raw: bool = False
) -> List["DataSourceWithDatasetUid"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/data-sources",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DataSourceWithDatasetUid"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DataSourceWithDatasetUid']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DataSourceWithDatasetUid.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import PatchDatasourcePayload


def patch_datasource_datasources__datasource_uid__patch(
    datasource_uid: int,
    *,
    body: PatchDatasourcePayload,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasources/{datasource_uid}",
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


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import AsyncJobResponse
from ..types import UNSET, Unset


@overload
def peek_datasource_by_path_peek_data_source_get(
    *,
    workspace_uid: Union[Unset, int] = 1,
    source_type: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    data_connector_config_uid: Union[Unset, int] = UNSET,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def peek_datasource_by_path_peek_data_source_get(
    *,
    workspace_uid: Union[Unset, int] = 1,
    source_type: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    data_connector_config_uid: Union[Unset, int] = UNSET,
    raw: Literal[False] = False,
) -> AsyncJobResponse: ...


def peek_datasource_by_path_peek_data_source_get(
    *,
    workspace_uid: Union[Unset, int] = 1,
    source_type: Union[Unset, str] = UNSET,
    path: Union[Unset, str] = UNSET,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    data_connector_config_uid: Union[Unset, int] = UNSET,
    raw: bool = False,
) -> AsyncJobResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params["source_type"] = source_type

    params["path"] = path

    params["truncate_texts"] = truncate_texts

    params["return_snorkel_gen_uid_as_col"] = return_snorkel_gen_uid_as_col

    params["data_connector_config_uid"] = data_connector_config_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/peek-data-source",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AsyncJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AsyncJobResponse
        response_200 = AsyncJobResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any, Union, overload

import requests
from typing_extensions import Literal

from ..models import AsyncJobResponse
from ..types import UNSET, Unset


@overload
def peek_datasource_data_sources__datasource_uid__peek_get(
    datasource_uid: int,
    *,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def peek_datasource_data_sources__datasource_uid__peek_get(
    datasource_uid: int,
    *,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    raw: Literal[False] = False,
) -> AsyncJobResponse: ...


def peek_datasource_data_sources__datasource_uid__peek_get(
    datasource_uid: int,
    *,
    truncate_texts: Union[Unset, bool] = True,
    return_snorkel_gen_uid_as_col: Union[Unset, bool] = False,
    raw: bool = False,
) -> AsyncJobResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["truncate_texts"] = truncate_texts

    params["return_snorkel_gen_uid_as_col"] = return_snorkel_gen_uid_as_col

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-sources/{datasource_uid}/peek",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> AsyncJobResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as AsyncJobResponse
        response_200 = AsyncJobResponse.from_dict(response)

        return response_200

    return _parse_response(response)


from typing import Any

from ..models import (
    DataSourcePrepResponseModel,
    PrepAndIngestDatasourceRequest,
)


def prep_and_ingest_datasource_datasets__dataset_uid__prep_data_sources_post(
    dataset_uid: int,
    *,
    body: PrepAndIngestDatasourceRequest,
) -> DataSourcePrepResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/prep-data-sources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> DataSourcePrepResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as DataSourcePrepResponseModel
        response_202 = DataSourcePrepResponseModel.from_dict(response)

        return response_202

    return _parse_response(response)


from typing import Any

from ..models import PutDatasource, PutDatasourceResponse


def put_datasource_data_sources__datasource_uid__put(
    datasource_uid: int,
    *,
    body: PutDatasource,
) -> PutDatasourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/data-sources/{datasource_uid}",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.put(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> PutDatasourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as PutDatasourceResponse
        response_201 = PutDatasourceResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import (
    SplitDataSourcesRequest,
    SplitDataSourcesResponseModel,
)


def split_datasources_datasets__dataset_uid__split_data_sources_post(
    dataset_uid: int,
    *,
    body: SplitDataSourcesRequest,
) -> SplitDataSourcesResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/split-data-sources",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> SplitDataSourcesResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as SplitDataSourcesResponseModel
        response_201 = SplitDataSourcesResponseModel.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import (
    IngestAndSwapDatasourcePayload,
    IngestAndSwapDatasourceResponse,
)


def swap_datasource_datasets__dataset_uid__datasources__datasource_uid__swap_post(
    dataset_uid: int,
    datasource_uid: int,
    *,
    body: IngestAndSwapDatasourcePayload,
) -> IngestAndSwapDatasourceResponse:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/datasources/{datasource_uid}/swap",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> IngestAndSwapDatasourceResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as IngestAndSwapDatasourceResponse
        response_201 = IngestAndSwapDatasourceResponse.from_dict(response)

        return response_201

    return _parse_response(response)


from typing import Any

from ..models import (
    BodyUploadDatasourceDatasetsDatasetUidUploadPost,
    UploadDatasourceResponseModel,
)


def upload_datasource_datasets__dataset_uid__upload_post(
    dataset_uid: int,
    *,
    body: BodyUploadDatasourceDatasetsDatasetUidUploadPost,
) -> UploadDatasourceResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/upload",
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UploadDatasourceResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UploadDatasourceResponseModel
        response_201 = UploadDatasourceResponseModel.from_dict(response)

        return response_201

    return _parse_response(response)
