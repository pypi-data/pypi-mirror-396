import asyncio
import io
import os
import posixpath
import re
from typing import Any, AsyncGenerator, Optional, Tuple, Union
from urllib.parse import urlparse, urlunparse

from fsspec import Callback
from fsspec.asyn import sync_wrapper
from fsspec.implementations.http import (
    DEFAULT_CALLBACK,
    HTTPFileSystem,
)
from fsspec.utils import nullcontext

from snorkelai.sdk.context.constants import html_link_re, plain_link_re
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel SDK context")

import json
import uuid
from hashlib import sha256

from aiohttp import ClientError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


# BytesIO wrapper with fsspec async support for buffering data.
class AsyncBytesIO(io.BytesIO):
    def __init__(
        self,
        *args: Any,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.loop = loop


# File-like object that can handle writing to storage-api
class HTTPFile:
    def __init__(self, fs: HTTPFileSystem, path: str, **kwargs: Any):
        self.fs = fs
        self.path = path
        self._buffer = AsyncBytesIO(loop=fs.loop)
        self.loop = fs.loop
        self.kwargs = kwargs

    def write(self, data: Union[str, bytes]) -> int:
        if isinstance(data, str):
            data = data.encode()  # Convert string to bytes
        return self._buffer.write(data)

    def close(self) -> None:
        self._buffer.seek(0)
        self.fs.put_file(self._buffer, self.path, **self.kwargs)
        self._buffer.close()

    # Supports context manager
    def __enter__(self) -> "HTTPFile":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


# Adds async support to io.IOBase file-like objects to make them fsspec-compatible.
class AsyncIOWrapper(io.IOBase):
    def __init__(
        self, file_obj: io.IOBase, loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        super().__init__()
        self._file = file_obj
        self.loop = loop

    def read(self, size: Optional[int] = -1) -> bytes:
        data = self._file.read(size)
        if isinstance(data, str):
            data = data.encode()
        return data


class HTTPFileSystemOverride(HTTPFileSystem):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    async def resolve_async(self, url: str) -> str:
        session = await self.set_session()
        async with session.get(self.encode_url(url), **self.kwargs) as resp:
            self._raise_not_found_for_status(resp, url)
            text = await resp.text()

            return text

    resolve = sync_wrapper(resolve_async)

    def put_file(
        self,
        lpath: Any,
        rpath: str,
        callback: Callback = DEFAULT_CALLBACK,
        **kwargs: Any,
    ) -> None:
        """
        Override of HTTPFileSystem.put_file to support multipart upload.
        Copy a file from local filesystem to remote storage.

        Args:
            lpath: Local path or file-like object to upload. Can be a string path
                  or an IO object (e.g., BytesIO, StringIO).
            rpath: Remote path where the file will be stored.
            callback: Progress callback object to track upload progress.
                     Defaults to DEFAULT_CALLBACK.
            **kwargs: Additional arguments passed to the upload process.

        Returns:
            None
        """
        if not isinstance(lpath, io.IOBase) and os.path.isdir(lpath):
            self.makedirs(rpath, exist_ok=True)
            return None

        self.mkdirs(os.path.dirname(rpath), exist_ok=True)

        # Wrap io.IOBase objects in a AsyncIOWrapper to set the event loop
        if isinstance(lpath, io.IOBase):
            lpath = AsyncIOWrapper(lpath, loop=self.loop)

        sync_wrapper(self._put_file)(lpath, rpath, callback, **kwargs)

    # The underlying HTTPFileSystem._put_file implementation supports uploading with
    # an IO buffer object. However, invoking this logic through the public put() API
    # results in errors. Create an override class to expose the logic of _put_file() directly.
    # This implementation also supports multipart uploads. The default implementation
    # streams the data directly into storage-api's upload endpoint as one large batch. This
    # function breaks the upload into chunks and uploads each chunk separately and
    # asynchronously into a temp folder. It then completes the multipart upload by calling the
    # /upload/complete/{file_path} endpoint to merge all parts of the temp folder into a single file.
    async def _put_file(
        self,
        lpath: Union[str, AsyncIOWrapper],
        rpath: str,
        callback: Callback = DEFAULT_CALLBACK,
        method: str = "post",
        **kwargs: Any,
    ) -> None:
        async def gen_chunks(
            calculated_chunk_size: int,
        ) -> AsyncGenerator[Tuple[int, bytes], None]:
            chunk_num = 0
            chunk = f.read(calculated_chunk_size)
            while chunk:
                yield chunk_num, chunk
                chunk = f.read(calculated_chunk_size)
                chunk_num += 1

        kw = self.kwargs.copy()
        kw.update(kwargs)
        session = await self.set_session()

        meth = getattr(session, method)
        method = method.lower()
        if method not in {"post", "put"}:
            raise ValueError(
                f"method has to be either 'post' or 'put', not: {method!r}"
            )

        # Support passing arbitrary file-like objects
        # and use them instead of streams.
        if isinstance(lpath, AsyncIOWrapper):
            context = nullcontext(lpath)
            use_seek = False  # might not support seeking
        else:
            context = open(lpath, "rb")
            use_seek = True

        with context as f:
            file_size = None
            if use_seek:
                file_size = f.seek(0, 2)
                callback.set_size(file_size)
                f.seek(0)
            else:
                file_size = getattr(f, "size", None)
                callback.set_size(file_size)

            upload_tasks = []
            multipart_upload = MultipartUpload(rpath, self, meth, callback, **kw)
            chunk_size = 5 * 2**20  # 5 MB

            async for chunk_num, chunk in gen_chunks(chunk_size):
                upload_tasks.append(multipart_upload.upload_chunk(chunk_num, chunk))

            # complete multipart upload
            try:
                await asyncio.gather(*upload_tasks)
                await multipart_upload.complete_multipart(len(upload_tasks))
            except Exception as e:
                await multipart_upload.complete_multipart(len(upload_tasks), True)
                raise Exception(
                    f"Failed to complete multipart upload for {rpath}"
                ) from e

    # Override fsspec's open() to support write mode
    def open(
        self,
        path: str,
        mode: str = "rb",
        block_size: Optional[int] = None,
        cache_options: Optional[dict] = None,
        compression: Optional[str] = None,
        **kwargs: Any,
    ) -> Union[io.IOBase, HTTPFile]:
        if mode in {"w", "wb"}:
            logger.info(f"Writing file via Storage API: {path}")
            return HTTPFile(self, path, **kwargs)

        return super().open(
            path,
            mode,
            block_size=block_size,
            cache_options=cache_options,
            compression=compression,
            **kwargs,
        )

    # Similarly, this function is taken from HTTPFileSystem and overridden. The original version
    # expects that all returned urls have the input url as a prefix, which is not the case
    # for new files that are workspace-scoped (i.e. since "workspace-#" is inserted in the
    # path). For now, override this behavior to accept any returned path as valid output.
    # We can eventually remove this once the entire system has been migrated to be implicitly
    # workspace-aware, but for backwards compatibility reasons now, we are returning the full
    # path with an explicit workspace. At this point, we may want to consider just implementing
    # our own custom HTTPFileSystem rather than using the fsspec version. These custom
    # overrides are tech debt and may provide fsspec upgrade challenges.
    async def _ls_real(self, url: str, detail: bool = True, **kwargs: Any) -> Any:
        # ignoring URL-encoded arguments
        kw = self.kwargs.copy()
        kw.update(kwargs)
        logger.debug(url)
        session = await self.set_session()
        async with session.get(self.encode_url(url), **self.kwargs) as r:
            self._raise_not_found_for_status(r, url)
            text = await r.text()
        if self.simple_links:
            links = plain_link_re.findall(text) + [
                u[2] for u in html_link_re.findall(text)
            ]
        else:
            links = [u[2] for u in html_link_re.findall(text)]
        out = set()
        parts = urlparse(url)
        for l in links:
            if isinstance(l, tuple):
                l = l[1]
            if l.startswith("/") and len(l) > 1:
                # absolute URL on this server
                l = f"{parts.scheme}://{parts.netloc}{l}"
            if l.startswith("http"):
                out.add(l)
            elif l not in {"..", "../"}:
                # Ignore FTP-like "parent"
                out.add("/".join([url.rstrip("/"), l.lstrip("/")]))
        if not out and url.endswith("/"):
            out = await self._ls_real(url.rstrip("/"), detail=False)
        if detail:
            return [
                {
                    "name": u,
                    "size": None,
                    "type": "directory" if u.endswith("/") else "file",
                }
                for u in out
            ]
        else:
            return sorted(out)


class MultipartUpload:
    """Manages uploading and combining file chunks for multipart uploads.

    Provides functions to upload individual chunks and combine them into the final file.

    Attributes:
        temp_folder: Unique temporary folder name for storing chunks
        rpath: Remote path where the final file will be stored
        _http_fs: HTTP filesystem interface for storage operations
        _method: HTTP method for upload operations
        _callback: Progress callback for tracking upload status
    """

    storage_api_upload_pattern = r"(.*?)/upload/(.+)$"

    def __init__(
        self,
        rpath: str,
        http_fs: HTTPFileSystemOverride,
        method: Any,
        callback: Callback,
        **kw: Any,
    ):
        self.kw = kw
        self.temp_folder = f"temp-multipart-{uuid.uuid4().hex}"
        self.rpath = rpath
        self._http_fs = http_fs
        self._method = method
        self._callback = callback

    # Makes sure the path is within the base path and does not contain restricted patterns
    def sanitize_path(self, relative_path: str) -> str:
        restricted_patterns = [r"temp-multipart-\w*"]

        for pattern in restricted_patterns:
            if re.search(pattern, relative_path):
                raise ValueError(
                    f"Invalid path: Path contains restricted pattern '{pattern}'"
                )

        # Normalize the path and check if it attempts to navigate up
        full_path = os.path.normpath(relative_path)
        if ".." in full_path.split(os.path.sep):
            raise ValueError(
                "Invalid path: Navigation outside the directory is not allowed."
            )

        return full_path

    # Returns temporary storage URL for multipart upload chunks
    def get_temp_folder_part_url(self, rpath: str) -> str:
        match = re.match(self.storage_api_upload_pattern, rpath)

        if match:
            base_url, file_path = match.groups()
            sanitized_path = self.sanitize_path(file_path)
            temp_folder_url = f"{base_url}/upload/{self.temp_folder}/{sanitized_path}"
            return temp_folder_url
        else:
            raise ValueError(f"Invalid rpath format: {rpath}")

    # Uploads chunk to temp folder for multipart upload with retry upon failure
    async def upload_chunk(self, chunk_num: int, chunk: bytes) -> str:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((ClientError, asyncio.TimeoutError)),
            reraise=True,
        )
        async def _upload_chunk_with_retry() -> str:
            temp_folder_url = self.get_temp_folder_part_url(self.rpath)
            file_part_path = f"{temp_folder_url}.part{chunk_num}"
            chunk_checksum = sha256(chunk).hexdigest()

            # Add checksum header for data integrity verification
            self.kw["headers"] = self.kw.get("headers", {})
            self.kw["headers"]["X-Checksum-Sha256"] = chunk_checksum

            async with self._method(
                self._http_fs.encode_url(file_part_path), data=chunk, **self.kw
            ) as resp:
                self._http_fs._raise_not_found_for_status(resp, file_part_path)
            return file_part_path

        try:
            self._callback.relative_update(len(chunk))
            return await _upload_chunk_with_retry()
        except Exception as e:
            logger.exception(
                f"Failed to upload chunk {chunk_num} after all retries.",
            )
            raise e

    # Updates /upload/ url to /upload-complete/ for complete_multipart
    def update_to_upload_complete_url(self, url: str) -> str:
        parsed = urlparse(url)

        # Change storage-api:<port>/upload/ to storage-api:<port>/upload-complete/
        match = re.match(self.storage_api_upload_pattern, parsed.path)

        if match:
            base_url, file_path = match.groups()
            new_path = f"{base_url}/upload-complete/{file_path}"
            parsed = parsed._replace(path=new_path)

        return urlunparse(parsed)

    # Completes multipart upload with retry upon failure
    async def complete_multipart(self, num_chunks: int, failed: bool = False) -> str:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((ClientError, asyncio.TimeoutError)),
            reraise=True,
        )
        async def _complete_multipart_retry(is_failed: bool) -> str:
            logger.info(f"Completing multipart upload for {self.rpath}")
            payload = {
                "temp_folder": self.temp_folder,
                "num_chunks": num_chunks,
                "failed": is_failed,
            }
            complete_url = self.update_to_upload_complete_url(self.rpath)
            logger.info(
                f"Complete multipart upload URL: {complete_url} for {self.rpath}"
            )

            url = self._http_fs.encode_url(complete_url)
            json_payload = json.dumps(payload)
            request_kwargs = self.kw.copy()

            request_kwargs["headers"]["Content-Type"] = "application/json"
            request_kwargs["data"] = json_payload

            async with self._method(url, **request_kwargs) as resp:
                self._http_fs._raise_not_found_for_status(resp, complete_url)

            return complete_url

        try:
            return await _complete_multipart_retry(is_failed=failed)
        except Exception as e:
            logger.exception("Failed to complete multipart upload.")
            # Attempt to clean up temp folder
            try:
                return await _complete_multipart_retry(is_failed=True)
            except Exception as clean_up_exception:
                logger.exception(
                    "Failed to clean up temp folders for multipart upload.",
                )
                raise clean_up_exception


def join_url(url_base: str, *paths: str) -> str:
    # Remove leading slashes from all path fragments
    cleaned_fragments = [fragment.lstrip("/") for fragment in paths]

    combined_path = posixpath.join(url_base.rstrip("/"), *cleaned_fragments)

    return combined_path
