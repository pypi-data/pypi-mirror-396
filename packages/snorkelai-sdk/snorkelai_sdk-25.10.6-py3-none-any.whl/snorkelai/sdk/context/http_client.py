import json
import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import requests

from snorkelai.sdk.context.constants import API_KEY_ENV_VAR, API_KEY_FILE_ENV_VAR
from snorkelai.sdk.context.file_watcher import FileWatcher
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel SDK context")


class HTTPClient:
    def __init__(
        self,
        url_base: str,
        requests_hook: Any = None,
        api_key: Optional[str] = None,
        debug: bool = False,
    ):
        self._watcher: Optional[FileWatcher] = None
        self.url_base = url_base
        if requests_hook is None:
            requests_hook = requests
        self.requests_hook = requests_hook
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
        self._api_key = api_key
        if not self._api_key:
            logger.warning(
                "No API key provided, and only requests that don't require "
                "authentication will succeed. Generate an API key from the "
                "user settings menu and provide it to the snorkelflow SDK "
                "by setting the ${SNORKEL_PLATFORM_API_KEY} environment variable "
                "or using the api_key parameter."
            )
        self.set_debug(debug)

    def __del__(self) -> None:
        if self._watcher:
            self._watcher.__del__()

    def _update_api_key(self, api_key: str) -> None:
        self._api_key = api_key

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key

    # enable detail and stacktrace in error message if debug is set to True
    def set_debug(self, debug: bool) -> None:
        self.debug = debug

    def _auth_headers(self) -> Dict[str, str]:
        if self._api_key is None:
            return {}
        return {"Authorization": f"key {self._api_key}"}

    def _url(self, endpoint: str) -> str:
        if self.url_base:
            # TODO: Standardize endpoint to have a leading slash.
            if endpoint.startswith("/"):
                return f"{self.url_base}{endpoint}"
            else:
                return f"{self.url_base}/{endpoint}"
        return endpoint

    def _parse_error_message(self, text: str) -> str:
        try:
            # SnorkelFlowAPIException: Use "detail + metadata" if in debug mode
            # otherwise use user_friendly_message or detail if user_friendly_message not available
            message = json.loads(text)
            message = (
                self._get_debug_error_message(message)
                if self.debug
                else (message.get("user_friendly_message") or message.get("detail"))
            ) or text
        except Exception:
            message = text
        return message

    def _get_debug_error_message(self, message: Dict[str, Any]) -> Optional[str]:
        if message.get("detail") is None or message.get("metadata") is None:
            return None
        debug_message = dict(
            detail=message.get("detail"),
            # metadata contains stacktrace which helps debug
            metadata=message.get("metadata"),
        )
        return json.dumps(debug_message, indent=True)

    def _dumps(self, json_data: Optional[Dict[str, Any]]) -> str:
        if json_data:
            return json.dumps(json_data)
        return ""

    def get(
        self,
        endpoint: str,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, Any]]]] = None,
        raw: bool = False,
    ) -> Any:
        """The `raw` parameter allows one to receive the raw `requests.Response` object
        (when the default requests_hook is used).
        This is useful if the response is either very large or isn't encoded as json.

        >>> client = HTTPClient(...)
        >>> r = client.get(url, raw=True)
        >>> with open(tmp_file, 'wb') as f:
        >>>     f.write(r.content)
        """
        url = self._url(endpoint)
        response = self.requests_hook.get(
            url, params=params, headers=self._auth_headers()
        )
        if not 200 <= response.status_code < 300:
            raise requests.HTTPError(
                f"Error {response.status_code} in API GET {url}: {self._parse_error_message(response.text)}",
                response=response,
            )
        if raw:
            return response
        return response.json() if response.content else None

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        safe_encode: bool = False,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, str]]]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """safe_encode
        We will use json.dumps(..) instead of the requests-internal json encoder
        as this adds support for np.nan, np.inf, etc.
        """
        url = self._url(endpoint)
        if safe_encode:
            response = self.requests_hook.post(
                url,
                data=self._dumps(json),
                params=params,
                headers=self._auth_headers(),
                files=files,
            )
        else:
            response = self.requests_hook.post(
                url, json=json, params=params, headers=self._auth_headers(), files=files
            )
        if response.request.method == "GET":
            # This happens when it is redirected from http to https
            raise requests.HTTPError(
                "A redirect from http to https was detected. "
                "Please set the protocol as 'https' when initializing SnorkelSDKContext."
            )
        if not 200 <= response.status_code < 300:
            raise requests.HTTPError(
                f"Error {response.status_code} in API POST {url}: {self._parse_error_message(response.text)}",
                response=response,
            )
        return response.json() if response.content else None

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, str]]]] = None,
    ) -> Any:
        url = self._url(endpoint)
        response = self.requests_hook.put(
            url, json=json, params=params, headers=self._auth_headers()
        )
        if not 200 <= response.status_code < 300:
            raise requests.HTTPError(
                f"Error {response.status_code} in API PUT {url}: {self._parse_error_message(response.text)}",
                response=response,
            )
        return response.json() if response.content else None

    def delete(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, str]]]] = None,
    ) -> Any:
        url = self._url(endpoint)
        response = self.requests_hook.request(
            "DELETE", url, json=json, params=params, headers=self._auth_headers()
        )
        if not 200 <= response.status_code < 300:
            raise requests.HTTPError(
                f"Error {response.status_code} in API DELETE {url}: {self._parse_error_message(response.text)}",
                response=response,
            )
        return response.json() if response.content else None

    def patch(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Union[Dict[str, Any], List[Tuple[str, str]]]] = None,
    ) -> Any:
        """Create patch method"""
        url = self._url(endpoint)
        response = self.requests_hook.patch(
            url, json=json, params=params, headers=self._auth_headers()
        )
        if not 200 <= response.status_code < 300:
            raise requests.HTTPError(
                f"Error {response.status_code} in API PATCH {url}: {self._parse_error_message(response.text)}",
                response=response,
            )
        return response.json() if response.content else None
