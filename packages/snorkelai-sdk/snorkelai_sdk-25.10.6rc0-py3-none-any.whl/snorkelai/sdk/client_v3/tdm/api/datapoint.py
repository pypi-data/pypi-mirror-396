# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, Union, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import GetDatasetDatapointsResponse
from ..types import UNSET, Unset


@overload
def get_datapoints_datasets__dataset_uid__datapoints_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    filter_config_str: Union[Unset, str] = "all",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[True],
) -> requests.Response: ...


@overload
def get_datapoints_datasets__dataset_uid__datapoints_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    filter_config_str: Union[Unset, str] = "all",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: Literal[False] = False,
) -> GetDatasetDatapointsResponse: ...


def get_datapoints_datasets__dataset_uid__datapoints_get(
    dataset_uid: int,
    *,
    split: Union[Unset, str] = UNSET,
    filter_config_str: Union[Unset, str] = "all",
    limit: Union[Unset, int] = UNSET,
    offset: Union[Unset, int] = 0,
    raw: bool = False,
) -> GetDatasetDatapointsResponse | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["split"] = split

    params["filter_config_str"] = filter_config_str

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/datasets/{dataset_uid}/datapoints",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> GetDatasetDatapointsResponse:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as GetDatasetDatapointsResponse
        response_200 = GetDatasetDatapointsResponse.from_dict(response)

        return response_200

    return _parse_response(response)
