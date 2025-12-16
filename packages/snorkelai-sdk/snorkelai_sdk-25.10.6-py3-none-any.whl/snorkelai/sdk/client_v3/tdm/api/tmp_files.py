# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import (
    BodyUploadTmpFilesUploadPost,
    UploadFileResponseModel,
)


def upload_tmp_files_upload_post(
    *,
    body: BodyUploadTmpFilesUploadPost,
) -> UploadFileResponseModel:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": "/tmp_files/upload",
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> UploadFileResponseModel:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as UploadFileResponseModel
        response_201 = UploadFileResponseModel.from_dict(response)

        return response_201

    return _parse_response(response)
