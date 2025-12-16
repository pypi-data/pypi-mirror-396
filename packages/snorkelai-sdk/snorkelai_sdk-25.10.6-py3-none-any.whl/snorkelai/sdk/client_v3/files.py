import os
import re
from typing import Any, Dict, List, Tuple
from urllib.parse import unquote, urlparse, urlunparse

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


# removes minio:// from path - will be updated after dual mode!
def _preprocess_minio_path(path: str) -> str:
    if path.startswith("minio://"):
        return path.replace("minio://", "")
    else:
        return path


# decode whitespace encodings in path
def _decode_path(path: str) -> str:
    return "/".join(unquote(part) for part in path.split("/"))


def upload_file(
    local_path: str,
    remote_path: str,
) -> str:
    """Uploads a file to the Snorkel Files Store.
    Both absolute paths (ex. minio://workspace-1/file.txt) and relative paths (ex. file.txt, workspace-1/file.txt) are supported.

    Warning
    -------
    If you're including the workspace prefix in the remote path, the workspace prefix (workspace-{#}) must match the current workspace.
    Relative paths will be resolved by removing the workspace prefix: workspace-1/file.txt -> file.txt.

    Example
    --------

    .. testcode::

        local_path = "/home/user/file.txt"
        remote_path = "file.txt"

        # File will be uploaded to minio://workspace-{current-workspace-id}/file.txt
        sai.upload_file(local_path, remote_path)

        # These calls will raise a ValueError
        sai.upload_file(local_path, "minio://workspace-{not-current-workspace-id}/file.txt")
        sai.upload_file(local_path, "workspace-{not-current-workspace-id}/file.txt")


    Parameters
    ----------
    local_path
        Path to file to be uploaded
    remote_path
        File path in Snorkel Files Store to upload file to

    Returns
    -------
    str
        The uploaded file path

    """
    ctx = SnorkelSDKContext.get_global()

    remote_path = _preprocess_minio_path(remote_path)
    uploaded_file = ctx.storage_client.upload(local_path, remote_path)
    return uploaded_file


def upload_dir(
    local_path: str,
    remote_path: str,
) -> Tuple[List[str], str]:
    """Uploads a local directory to the Snorkel Files Store.
    Both absolute paths (ex. minio://workspace-1/data_dir) and relative paths (ex. data_dir, workspace-1/data_dir) are supported.

    Warning
    -------
    If you're including the workspace prefix in the remote path, the workspace prefix (workspace-{#}) must match the current workspace.
    Relative paths will be resolved by removing the workspace prefix: workspace-1/data_dir -> data_dir.

    Example
    --------

    .. testcode::

        local_path = "/home/user/data_dir"
        remote_path = "data_dir"

        # Directory will be uploaded to minio://workspace-{current-workspace-id}/data_dir
        sai.upload_dir(local_path, remote_path)

        # These calls will raise a ValueError
        sai.upload_dir(local_path, "minio://workspace-{not-current-workspace-id}/data_dir")
        sai.upload_dir(local_path, "workspace-{not-current-workspace-id}/data_dir")


    Parameters
    ----------
    local_path
        Directory containing files to be uploaded.
    remote_path
        Remote directory on Snorkel Files Store to upload files to.

    Returns
    -------
    Tuple[List[str], str]
        Tuple containing:
            - List of uploaded file paths
            - Uploaded directory path

    """
    ctx = SnorkelSDKContext.get_global()
    storage_client = ctx.storage_client

    minio_paths = []
    remote_path = _preprocess_minio_path(remote_path)

    # Walk through all files in the specified directory and subdirectories
    for root, _, files in os.walk(local_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            # Compute remote path correctly by stripping the root directory
            remote_file_path = os.path.join(
                remote_path, _strip_root_path(local_file_path, local_path)
            )
            # Upload each file and store the resulting path
            uploaded_file_path = storage_client.upload(
                local_file_path, remote_file_path
            )
            minio_paths.append(uploaded_file_path)

    # Ensure all uploaded paths are consistent
    if not minio_paths:
        raise ValueError("No files were uploaded.")

    # Compute the uploaded directory path based on the first uploaded file path
    minio_dir = _compute_dir(minio_paths, remote_path)

    return minio_paths, minio_dir


def _compute_dir(
    minio_paths: List[str],
    dir_to_upload: str,
) -> str:
    """Computes the remote directory path based on uploaded files' paths.

    Parameters
    ----------
    minio_paths
        List of uploaded file paths.
    dir_to_upload
        Local directory that was uploaded.

    Returns
    -------
    str
        The computed remote directory path.

    """
    # Regular expression to capture the workspace path prefix in Minio URLs
    prefix_re = re.compile(r"^(minio://workspace-\d+/)")

    if len(minio_paths) == 0:
        raise ValueError("No minio_paths provided.")

    # Extract the prefix from the first uploaded file path
    minio_path = minio_paths[0]
    match = prefix_re.match(minio_path)
    if not match:
        raise ValueError(f"Unexpected path format: {minio_path}")

    # Grab the workspace from the prefix
    prefix = match.group(1)
    workspace_prefix = re.compile(r"workspace-\d+")
    match = workspace_prefix.search(prefix)

    if not match:
        raise ValueError(f"Unexpected path format: {minio_path}")

    workspace_id = match.group(0)
    workspace_remove = re.compile(f"^{workspace_id}/")
    dir_sub = re.sub(workspace_remove, "", dir_to_upload)

    return os.path.join(prefix, dir_sub)


def _strip_root_path(file_path: str, root_path: str) -> str:
    """Strips the root path from the file path to compute the relative path.

    Parameters
    ----------
    file_path
        The full path to the file.
    root_path
        The root directory to be stripped from the file path.

    Returns
    -------
    str
        The relative file path.

    """
    # Normalize both paths to avoid issues with trailing slashes or inconsistent formats
    file_path = os.path.normpath(file_path)
    root_path = os.path.normpath(root_path)

    # Validate that the file path starts with the root path
    if not file_path.startswith(root_path):
        raise ValueError(
            f"File path {file_path} does not start with root path {root_path}"
        )

    # Remove the root path and return the relative path
    return os.path.relpath(file_path, root_path)


def download_file(remote_path: str, local_path: str) -> None:
    """Downloads remote file from Snorkel Files Store to local file.
    Both absolute paths (ex. minio://workspace-1/data/file.txt) and relative paths (ex. data/file.txt, workspace-1/data/file.txt) are supported.

    Warning
    -------
    If you're including the workspace prefix in the remote path, the workspace prefix (workspace-{#}) must match the current workspace.
    Relative paths will be resolved by removing the workspace prefix: workspace-1/file.txt -> file.txt.

    Example
    --------

    .. testcode::

        remote_path = "minio://workspace-1/data/file.txt"
        local_path = "/home/user/file.txt"

        # File will be downloaded to /home/user/file.txt
        sai.download_file(remote_path, local_path)

        # These calls will raise a ValueError
        sai.download_file("minio://workspace-{not-current-workspace-id}/data/file.txt", local_path)
        sai.download_file("workspace-{not-current-workspace-id}/data/file.txt", local_path)


    Parameters
    ----------
    remote_path
        Path of file to be downloaded
    local_path
        Local path to download file to

    Returns
    -------
    None

    """
    ctx = SnorkelSDKContext.get_global()
    ctx.storage_client.download(_preprocess_minio_path(remote_path), local_path)


def download_dir(remote_path: str, local_path: str) -> None:
    """Downloads remote directory from Snorkel Files Store to local directory.
    Files and subdirectories inside the remote directory will be placed directly in the local directory.
    Both absolute paths (ex. minio://workspace-1/data_dir) and relative paths (ex. data_dir, workspace-1/data_dir) are supported.

    Warning
    -------
    If you're including the workspace prefix in the remote path, the workspace prefix (workspace-{#}) must match the current workspace.
    Relative paths will be resolved by removing the workspace prefix: workspace-1/data_dir -> data_dir.

    Example
    --------

    .. testcode::

        remote_path = "minio://workspace-1/data_dir" # equivalent to "data_dir"
        local_path = "/home/user/download_dir"

        # Files and sub-directories under `remote_path` will be downloaded to /home/user/download_dir
        sai.download_dir(remote_path, local_path)

        # To preserve the directory name, you can specify the local path like this:
        sai.download_dir(remote_path, "/home/user/download_dir/data_dir")

        # These calls will raise a ValueError
        sai.download_dir("minio://workspace-{not-current-workspace-id}/data_dir", local_path)
        sai.download_dir("workspace-{not-current-workspace-id}/data_dir", local_path)


    Parameters
    ----------
    remote_path
        Path of remote directory to be downloaded
    local_path
        Local directory to download file to

    Returns
    -------
    None

    """
    ctx = SnorkelSDKContext.get_global()
    storage_client = ctx.storage_client

    # Normalise the incoming remote path (strip minio://, etc.)
    remote_path = _preprocess_minio_path(remote_path)

    # Make sure the destination root exists
    os.makedirs(local_path, exist_ok=True)

    # Walk the remote tree
    base_url, res = storage_client.walk(remote_path)

    # Ensure trailing slash so os.path.relpath() treats base_url as a directory
    if not base_url.endswith("/"):
        base_url += "/"

    for path, _, files in res:
        for file in files:
            # Full *encoded* remote path of this file
            remote_file_path = os.path.join(path, file)

            # Compute relative path using encoded strings only
            rel_path_encoded = os.path.relpath(remote_file_path, base_url)

            # Decode once for the on-disk path
            rel_path = _decode_path(rel_path_encoded)

            # Local destination
            target_path = os.path.join(local_path, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Download the file
            storage_client.download_path(
                _rewrite_ls_path_for_download(remote_file_path),
                target_path,
            )


def _rewrite_ls_path_for_download(path: str) -> str:
    parsed_url = urlparse(path)
    # Split the path and replace the first segment 'ls' with 'download'
    new_path = parsed_url.path.replace("/ls/", "/download/", 1)
    # Construct the new URL
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )
    return new_url


def list_dir(remote_path: str) -> List[Any]:
    """Lists files in remote directory from Snorkel Files Store.
    Both absolute paths (ex. minio://workspace-1/data_dir) and relative paths (ex. data_dir, workspace-1/data_dir) are supported.

    Warning
    -------
    If you're including the workspace prefix in the remote path, the workspace prefix (workspace-{#}) must match the current workspace.
    Relative paths will be resolved by removing the workspace prefix: workspace-1/data_dir -> data_dir.

    Example
    --------

    .. testcode::

        remote_path = "minio://workspace-1/data_dir" # equivalent to "data_dir"

        # Files in the remote directory will be listed
        sai.list_dir(remote_path)

        # These calls will raise a ValueError
        sai.list_dir("minio://{not-current-workspace-id}/data_dir")
        sai.list_dir("{not-current-workspace-id}/data_dir")


    Parameters
    ----------
    remote_path
        Path to directory to be listed

    Returns
    -------
    List[Any]
        List of files in specified remote directory

    """
    ctx = SnorkelSDKContext.get_global()
    list_path = ctx.storage_client.ls(_preprocess_minio_path(remote_path))
    return _process_list_output(list_path)


def _process_list_output(list_path: List[Any]) -> List[Dict[str, str]]:
    """Processes the output from storage_client.ls, stripping URL prefixes from names.

    Parameters
    ----------
    list_path : List[Any]
        The original list of dictionaries from storage_client.ls.

    Returns
    -------
    List[Dict[str, str]]
        Processed list with stripped URL prefixes in 'name' fields.

    """

    def strip_url_prefix(url: str) -> str:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split("/")
        try:
            ls_index = path_parts.index("ls")
            return "/".join(path_parts[ls_index + 1 :])
        except ValueError:
            # if the URL path returned contains no "ls" prefix, return the original path as is
            return parsed_url.path.lstrip("/")

    return [
        {
            "name": _decode_path(strip_url_prefix(item["name"])),
            "type": item.get("type"),
        }
        for item in list_path
    ]
