import os
from typing import Any, Union

from requests import Response

from snorkelai.sdk.context.ctx import SnorkelSDKContext
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel Flow context")


def _ensure_not_directory(destination_path: str) -> None:
    if os.path.isdir(destination_path):
        raise ValueError(
            f"destination_path '{destination_path}' is a directory, expected a file path."
        )


# Downloads artifact from storage-api to local file
def _download_artifact_to_file(url: str, destination_path: str) -> None:
    try:
        ctx = SnorkelSDKContext.get_global()
    except AttributeError:
        ctx = None

    if ctx and ctx.storage_client and ctx.storage_client.workspace_uid:
        os.makedirs(os.path.dirname(destination_path) or ".", exist_ok=True)
        _ensure_not_directory(destination_path)
        ctx.storage_client.download(url, destination_path)
    else:
        raise RuntimeError("No storage client found")


# Writes async generator to file
def _download_stream_to_file(stream: Any, destination_path: str) -> None:
    if not hasattr(stream, "iter_content"):
        raise TypeError("Must be a stream object with an iter_content method")

    os.makedirs(os.path.dirname(destination_path) or ".", exist_ok=True)
    _ensure_not_directory(destination_path)

    with open(destination_path, "wb") as f:
        f.writelines(stream.iter_content(chunk_size=8192))


def download_to_file(
    export_response: Union[dict, Response],
    destination_path: str,
) -> None:
    if isinstance(export_response, dict):
        if "flipper_job_id" in export_response:
            return  # RemoteExportResponse
        if "url" in export_response:
            _download_artifact_to_file(export_response["url"], destination_path)
            return  # LocalFileExportResponse

    # Otherwise, it's a StreamingResponse
    _download_stream_to_file(export_response, destination_path)
