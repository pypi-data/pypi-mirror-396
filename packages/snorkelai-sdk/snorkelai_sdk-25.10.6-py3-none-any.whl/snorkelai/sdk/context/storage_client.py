import io
import os
import pathlib
from typing import IO, Any, List, Optional, Tuple, Union

from snorkelai.sdk.context.constants import (
    API_KEY_ENV_VAR,
    API_KEY_FILE_ENV_VAR,
    DEFAULT_WORKSPACE_UID,
    workspace_pattern,
)
from snorkelai.sdk.context.file_watcher import FileWatcher
from snorkelai.sdk.context.http_storage_client import (
    HTTPFile,
    HTTPFileSystemOverride,
    join_url,
)
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel SDK context")


class StorageClient:
    def __init__(
        self,
        url_base: str = "",
        api_key: Optional[str] = None,
        workspace_uid: Optional[int] = None,
    ):
        self._watcher: Optional[FileWatcher] = None
        if api_key is None:
            apk_key_file = os.getenv(API_KEY_FILE_ENV_VAR)
            if apk_key_file:
                self._api_key_file = pathlib.Path(apk_key_file)
                if self._api_key_file.exists():
                    api_key = self._api_key_file.read_text().rstrip()
                    self._watcher = FileWatcher(
                        self._api_key_file, self._update_api_key
                    )
        if api_key is None:
            api_key = os.getenv(API_KEY_ENV_VAR)

        if not api_key:
            logger.warning(
                "No API key provided, and only requests that don't require "
                "authentication will succeed. Generate an API key from the "
                "user settings menu and provide it to the snorkelflow SDK "
                "by setting the ${SNORKEL_PLATFORM_API_KEY} environment variable "
                "or using the api_key parameter."
            )

        self._api_key = api_key
        self.url_base = url_base
        self.workspace_uid = (
            workspace_uid if workspace_uid is not None else DEFAULT_WORKSPACE_UID
        )

        # Prepare headers for HTTP filesystem
        headers = {"Authorization": f"key {self._api_key}"}

        self._http_filesystem = HTTPFileSystemOverride(
            headers=headers,
            params={"workspace_uid": self.workspace_uid},
        )

    def __del__(self) -> None:
        if self._watcher:
            self._watcher.__del__()

    def _update_api_key(self, api_key: str) -> None:
        # Preserve existing headers and update only the Authorization header
        current_headers = self._http_filesystem.kwargs.get("headers", {}).copy()
        current_headers["Authorization"] = f"key {api_key}"
        self._http_filesystem.kwargs["headers"] = current_headers
        self._api_key = api_key

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key

    def download(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        """Download a file from minio to the specified local path.

        Parameters
        ----------
        minio_bucket
            name of bucket on minio
        minio_path
            path on minio relative to bucket
        local_path
            local path of the downloaded file

        Returns
        -------
        None

        """
        remote_path = self._check_and_strip_scheme_and_workspace_prefix(remote_path)
        self.download_path(
            join_url(self.url_base, "download", remote_path),
            local_path,
        )

    def download_path(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        """Download a file based on its full url download path to the specified local path.
        e.g. http://storage-api:31315/download/path/to/file

        In general, the download() function should be used as a more convenient wrapper for
        specifying remote files for download.

        Parameters
        ----------
        remote_path
            full download url path for remote file to download
        local_path
            local path of the downloaded file

        Returns
        -------
        None

        """
        remote_path = self._check_and_strip_scheme_and_workspace_prefix(remote_path)
        self._http_filesystem.get(remote_path, local_path)

    def ls(
        self,
        file_path: str,
    ) -> List[Any]:
        """List the contents specified by the provided file path. The file path is a relative path
        relative to root e.g. "path/to/directory". If the provided file path is a file (rather than
        a directory), the returned array will return a single file result.

        Parameters
        ----------
        file_path
            relative path from the root dir

        Returns
        -------
            List[Any]
                List of dictionaries that contain the fields:
                {
                    "name": <full "ls" url to the file e.g. http://storage-api:31315/ls/path/to/file>,
                    "type": "file"|"dictionary"
                }

        """
        file_path = self._check_and_strip_scheme_and_workspace_prefix(file_path)
        return self._http_filesystem.ls(join_url(self.url_base, "ls", file_path))

    def resolve(
        self,
        path: str,
    ) -> str:
        return self._http_filesystem.resolve(join_url(self.url_base, "resolve", path))

    def walk(
        self,
        dir_path: str,
    ) -> Tuple[str, Any]:
        """Recursively walk through the contents of a directory

        Parameters
        ----------
        dir_path
            path to the directory to walk

        Returns
        -------
            Tuple[str, Any]
                First tuple value is the full "ls" url of the base directory
                    e.g. http://storage-api:31315/ls/path/to/dir
                Second tuple value is a generator, which returns tuple values of the foramt:
                    (
                        full "ls" url of current directory,
                        list of subdirectories in the current directory,
                        list of files in the current directory
                    )
                e.g.
                (
                    http://storage-api:31315/ls/path/to/dir,
                    ["subdir1", "subdir2"],
                    ["file1", "file2"]
                )

        """
        full_path = self.resolve(dir_path)
        return full_path, self._http_filesystem.walk(full_path)

    def _get_workspace_minio_path(self, minio_bucket: str, minio_path: str) -> str:
        return join_url("minio://", minio_bucket, minio_path)

    # Strips workspace prefix from path for consistent upload/download path resolution
    # Raises ValueError if workspace number does not match current workspace
    # Examples:
    #   workspace-{self.workspace_uid}/path/to/file -> path/to/file
    #   workspace-{not self.workspace_uid}/path/to/file -> ValueError
    # To be removed post migration
    def _check_and_strip_scheme_and_workspace_prefix(self, path: str) -> str:
        path = path.replace("minio://", "")
        if self.workspace_uid:
            match = workspace_pattern.match(path)

            if match:
                if match.group(0) == f"workspace-{self.workspace_uid}/":
                    return path[match.end() :]
                else:
                    raise ValueError(
                        f"Prefix {match.group(0)} does not match current workspace {self.workspace_uid}"
                    )

        return path

    def upload(
        self,
        local_path: Union[str, IO],
        remote_path: str,
    ) -> str:
        """Upload a file to the specified minio location.

        Parameters
        ----------
        file_to_upload
            File to upload - can be a path to a local file or an in-memory IO object
        remote_path
            Remote path to upload file to

        Returns
        -------
        str
            Full path to the uploaded file (for now, explicitly workspace-prefixed)

        """
        remote_path = self._check_and_strip_scheme_and_workspace_prefix(remote_path)

        # Handle IO objects with our custom override method
        if isinstance(local_path, io.IOBase):
            put_method = self._http_filesystem.put_file
        else:
            put_method = self._http_filesystem.put

        put_method(
            local_path,
            join_url(self.url_base, "upload", remote_path),
        )

        # Annoyingly, fsspec does not actually return the output from "put" upload, which would
        # have been a sensible way to get the uploaded file path. Instead, we need to manually
        # assume/rebuild the workspace-scoped path.
        # NOTE: For now, we expose the full workspace-scoped path because the rest of the application is
        # not updated to automatically handle workspace-scoping. This logic should be removed once the
        # rest of the application is updated, so we don't expose the workspace in the path to the user.
        return join_url(f"minio://workspace-{self.workspace_uid}/", remote_path)

    def _update_workspace_uid(
        self,
        new_workspace_uid: int,
    ) -> None:
        self._http_filesystem.kwargs["params"] = {"workspace_uid": new_workspace_uid}
        self.workspace_uid = new_workspace_uid

    def _update_requests_session(self, requests_session: Optional[Any]) -> None:
        """Update the requests session and extract User-Agent for HTTP filesystem headers."""
        headers = {"Authorization": f"key {self._api_key}"}

        if requests_session and hasattr(requests_session, "headers"):
            user_agent = requests_session.headers.get("User-Agent")
            if user_agent:
                headers["User-Agent"] = user_agent

        self._http_filesystem.kwargs["headers"] = headers

    def open(
        self, path: str, mode: str = "rb", **kwargs: Any
    ) -> Union[io.IOBase, HTTPFile]:
        """
        Open a file, delegating to the Storage API for remote operations.
        """
        logger.info(f"Opening file: {path} with mode: {mode}")

        if mode not in {"r", "rb", "w", "wb"}:
            raise ValueError(
                f"Unsupported mode: {mode}. Supported modes are 'r', 'rb', 'w', 'wb'."
            )

        remote_path = self._check_and_strip_scheme_and_workspace_prefix(path)

        if "w" in mode:
            path = join_url(self.url_base, "upload", remote_path)
        else:
            path = join_url(self.url_base, "download", remote_path)

        return self._http_filesystem.open(path, mode=mode, **kwargs)
