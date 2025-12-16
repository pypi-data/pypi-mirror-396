# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet,
)
from ..types import UNSET, Unset


@overload
def get_paginated_data_virtualized_dataset__virtualized_dataset_uid__data_get(
    virtualized_dataset_uid: int,
    *,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_paginated_data_virtualized_dataset__virtualized_dataset_uid__data_get(
    virtualized_dataset_uid: int,
    *,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    raw: Literal[False] = False,
) -> GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet: ...


def get_paginated_data_virtualized_dataset__virtualized_dataset_uid__data_get(
    virtualized_dataset_uid: int,
    *,
    offset: Union[Unset, int] = 0,
    limit: Union[Unset, int] = 100,
    raw: bool = False,
) -> (
    GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet
    | requests.Response
):
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["offset"] = offset

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/virtualized-dataset/{virtualized_dataset_uid}/data",
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
    ) -> GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet
        response_200 = GetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGetResponseGetPaginatedDataVirtualizedDatasetVirtualizedDatasetUidDataGet.from_dict(
            response
        )

        return response_200

    return _parse_response(response)
