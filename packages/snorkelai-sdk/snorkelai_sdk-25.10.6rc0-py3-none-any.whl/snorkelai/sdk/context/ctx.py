import importlib.metadata
import os
import warnings
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import requests

from snorkelai.sdk.context.constants import (
    BASE_URL_ENV_VAR,
    DEFAULT_WORKSPACE_NAME,
    DEFAULT_WORKSPACE_UID,
)
from snorkelai.sdk.context.http_client import HTTPClient
from snorkelai.sdk.context.storage_client import StorageClient
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Snorkel SDK context")


class SnorkelSDKContext:
    """The SnorkelSDKContext object provides client context for the Snorkel Flow SDK. It allows the Snorkel Flow SDK
    to recognize a Snorkel Flow instance by identifying Snorkel Flow's essential API services (TDM & Storage API) via
    user-provided parameters, a YAML config file, or a Snorkel Flow API key.

    Examples
    --------
    ::

        import snorkelai.sdk.client as sai
        ctx = sai.SnorkelSDKContext.from_endpoint_url(...)

    """

    _ctx: Optional["SnorkelSDKContext"] = None
    _workspace_name: str = DEFAULT_WORKSPACE_NAME

    def __init__(
        self,
        tdm_client: HTTPClient,
        storage_client: Optional[StorageClient] = None,
        workspace_name: Optional[str] = None,
        set_global: bool = True,
        debug: bool = False,
    ) -> None:
        """Initialize a SnorkelSDKContext."""
        sdk_session = requests.Session()
        sdk_session.headers.update({"User-Agent": _get_user_agent()})
        self._sdk_session = sdk_session

        self.tdm_client = tdm_client
        self._set_requests_hook_if_needed(self.tdm_client, sdk_session)

        if storage_client:
            storage_client._update_requests_session(sdk_session)
        self._storage_client = storage_client

        self.workspace_name = workspace_name or _find_default_workspace(self.tdm_client)
        self.set_debug(debug)

        if set_global:
            self.set_global(self)

    def __del__(self) -> None:
        if self.tdm_client:
            self.tdm_client.__del__()
        if self.storage_client:
            self.storage_client.__del__()

    @classmethod
    def set_global(cls, ctx: Optional["SnorkelSDKContext"] = None) -> None:
        """Set a SnorkelSDKContext object globally. This context object will be used by all Snorkel Platform SDK functions.

        Examples
        --------
        ::

            import snorkelai.sdk.client as sai
            ctx = sai.SnorkelSDKContext.from_endpoint_url(...)
            sai.SnorkelSDKContext.set_global(ctx)


        Parameters
        ----------
        ctx
            A context to set as global. If no context is provided, will attempt to create one with default parameters.

        """
        from snorkelai.sdk.utils.logging import get_logger

        logger = get_logger("Snorkel SDK context")

        if ctx is None:
            # Construct ctx that works with the in-platform notebook
            logger.info("No ctx is provided. Creating one with the default parameters.")
            endpoint = os.getenv(BASE_URL_ENV_VAR, "http://envoy-front-proxy:1080")
            cls._ctx = cls.from_endpoint_url(endpoint=endpoint)
        else:
            cls._ctx = ctx

    @classmethod
    def get_global(cls) -> "SnorkelSDKContext":
        """Retrieve the global SnorkelSDKContext object.

        Examples
        --------
        ::

            import snorkelai.sdk.client as sai
            ctx = sai.SnorkelSDKContext.get_global()


        Returns
        -------
        SnorkelSDKContext
            A SnorkelSDKContext object that can be used to interact with the TDM and Storage API clients directly.

        Raises
        ------
        AttributeError
            If no global context has been set.

        """
        if cls._ctx:
            return cls._ctx
        else:
            raise AttributeError(
                "No ctx has been set. Please create one and set it through SnorkelSDKContext.set_global"
            )

    @property
    def storage_client(self) -> StorageClient:
        if not self._storage_client:
            raise Exception("No Http Filesystem in Context.")

        return self._storage_client

    @property
    def workspace_name(self) -> str:
        """SnorkelSDKContext objects are only scoped to work in a particular workspace.

        Returns
        -------
        str
            The name of the workspace belonging to this context object.

        """
        return self._workspace_name

    @workspace_name.setter
    def workspace_name(self, workspace_name: str) -> None:
        # Update workspace scope for HttpFilesystem used for file access
        workspace_id = _get_workspace_uid(self.tdm_client, workspace_name)
        if self._storage_client:
            self._storage_client._update_workspace_uid(workspace_id)

        self._workspace_name = workspace_name

    # enable detail and stacktrace in error message if debug is set to True
    def set_debug(self, debug: bool) -> None:
        """Set the verbosity of warnings, details, and stacktraces

        Parameters
        ----------
        debug
            If True, SDK operations will print more verbose errors to the screen inside of the Python notebook.

        """
        self.tdm_client.set_debug(debug)
        self.debug = debug

    @classmethod
    def from_endpoint_url(
        cls,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        workspace_name: Optional[str] = None,
        set_global: bool = True,
        debug: bool = False,
        *args: tuple,
        **kwargs: Any,
    ) -> "SnorkelSDKContext":
        """Initialize a SnorkelSDKContext from keyword arguments.

        Examples
        --------
        ::

            # Instantiate with default kwargs and a custom url
            import snorkelai.sdk.client as sai
            ctx = sai.SnorkelSDKContext.from_endpoint_url("https://edge.k8s.g498.io/")


        ::

            # Instantiate with custom kwargs
            import snorkelai.sdk.client as sai
            ctx = sai.SnorkelSDKContext.from_endpoint_url(
                endpoint="https://edge.k8s.g498.io/",
                workspace_name="my-workspace",
            )


        ::

            # Instantiate with an API key
            import snorkelai.sdk.client as sai
            ctx = sai.SnorkelSDKContext.from_endpoint_url(
                endpoint="https://edge.k8s.g498.io/",
                api_key="my-api-key",
            )


        Parameters
        ----------
        endpoint
            The baseurl to a snorkelflow instance.
        workspace_name
            The workspace name, which determines the workspace a dataset and application will be created in and queried from.
        api_key
            The API key to use for the TDM and Storage API.
        set_global
            Whether to set the context as the global context, accessible across all notebooks in-platform.
        debug
            Whether to enable debug mode. Debug mode will print more verbose errors to the screen inside of the Python notebook.

        Returns
        -------
        SnorkelSDKContext
            A SnorkelSDKContext object that can be used to interact with the TDM and Storage API clients directly.

        """
        validate_arguments(*args, **kwargs)
        if not endpoint:
            endpoint = os.getenv(BASE_URL_ENV_VAR)
        if not endpoint:
            raise ValueError(
                f"must provide a valid endpoint argument or set {BASE_URL_ENV_VAR}"
            )
        url = urlparse(endpoint)
        # normalize the path
        path = url.path.rstrip("/")

        return cls(
            tdm_client=HTTPClient(
                url_base=f"{url.scheme}://{url.netloc}{path}/tdm-api",
                api_key=api_key,
            ),
            storage_client=_create_storage_client(
                url_base=f"{url.scheme}://{url.netloc}{path}/storage-api",
                api_key=api_key,
            ),
            workspace_name=workspace_name,
            set_global=set_global,
            debug=debug,
        )

    @classmethod
    def _from_dict(
        cls,
        tdm_kwargs: Dict[str, Any],
        storage_client_kwargs: Optional[Dict[str, Any]] = None,
        session_headers: Optional[Dict[str, str]] = None,
        set_global: bool = True,
        debug: bool = False,
    ) -> "SnorkelSDKContext":
        # Only create and set SDK session if we have session headers to restore
        if session_headers:
            sdk_session = requests.Session()
            sdk_session.headers.update(session_headers)
            # Configure clients to use the shared session
            tdm_kwargs["requests_hook"] = sdk_session

        return cls(
            tdm_client=HTTPClient(**tdm_kwargs),
            storage_client=(
                _create_storage_client(**storage_client_kwargs)
                if storage_client_kwargs
                else None
            ),
            set_global=set_global,
            debug=debug,
        )

    def _to_dict(self) -> Dict[str, Any]:
        if self.tdm_client is None:
            raise AttributeError(
                "tdm_client cannot be None. Please provide a valid HTTPClient"
            )

        kwargs: Dict[str, Any] = {"debug": self.debug}

        kwargs["tdm_kwargs"] = {
            "url_base": self.tdm_client.url_base,
            "api_key": self.tdm_client.api_key,
            "debug": self.tdm_client.debug,
        }

        # Save session headers if using sessions
        if hasattr(self.tdm_client.requests_hook, "headers"):
            kwargs["session_headers"] = dict(self.tdm_client.requests_hook.headers)

        if self._storage_client is not None:
            kwargs["storage_client_kwargs"] = {
                "url_base": self._storage_client.url_base,
                "api_key": self._storage_client.api_key,
                "workspace_uid": self._storage_client.workspace_uid,
            }

        return kwargs

    def _set_requests_hook_if_needed(
        self, client: HTTPClient, sdk_session: Any
    ) -> None:
        """Set the requests hook to use the SDK session if no hook is set.
        This allows users to provide their own session while ensuring a default
        session is available when needed.
        """
        user_agent = _get_user_agent()

        # Use SDK session when we can't set User-Agent headers directly
        if (
            not hasattr(client, "requests_hook")
            or client.requests_hook is None
            or client.requests_hook is requests
        ):
            client.requests_hook = sdk_session
        # For custom hooks or session-like objects, update the headers
        elif hasattr(client.requests_hook, "headers") and isinstance(
            client.requests_hook.headers, dict
        ):
            client.requests_hook.headers.update({"User-Agent": user_agent})


def _get_workspace_uid(tdm_client: HTTPClient, workspace_name: str) -> int:
    res = tdm_client.get("/workspaces", params={"workspace_name": workspace_name})
    workspaces = res.get("workspaces")
    for workspace in workspaces:
        if workspace.get("name") == workspace_name:
            return workspace.get("workspace_uid")

    raise ValueError(
        f"Workspace with name '{workspace_name}' not found or not accessible."
    )


def _create_storage_client(
    url_base: str = "",
    api_key: Optional[str] = None,
    workspace_uid: Optional[int] = None,
) -> StorageClient:
    return StorageClient(url_base, api_key, workspace_uid)


def _find_default_workspace(tdm_client: HTTPClient) -> str:
    # check for workspace named "default", return early in most cases
    from snorkelai.sdk.utils.logging import get_logger

    logger = get_logger("Snorkel SDK context")

    res: Dict[str, Any] = tdm_client.get(
        "/workspaces", {"workspace_name": DEFAULT_WORKSPACE_NAME}
    )
    workspaces: List[Dict[str, Any]] = res.get("workspaces", [])
    for workspace in workspaces:
        if workspace["name"] == DEFAULT_WORKSPACE_NAME:
            return DEFAULT_WORKSPACE_NAME
    # check remaining workspaces
    res = tdm_client.get("/workspaces")
    workspaces = res.get("workspaces", [])
    if len(workspaces) == 0:
        raise ValueError("Did not find a workspace that is accessible.")
    # Check for workspace with uid 1
    for workspace in workspaces:
        if workspace.get("workspace_uid") == DEFAULT_WORKSPACE_UID:
            return workspace["name"]
    # Set the first workspace found
    logger.info(
        f"Default workspace not found or accessible, using workspace '{workspaces[0]['name']}' as default."
    )
    return workspaces[0]["name"]


def _get_sdk_version() -> str:
    """Get version from environment variable or package metadata.
    Returns
    -------
    str
        The version string, or "0.0.0" if it cannot be determined.
    """
    # Try to get version from package metadata
    try:
        version = importlib.metadata.version("snorkel-sdk")
        if version and version != "0.0.0":
            return version
    except importlib.metadata.PackageNotFoundError:
        pass

    return "0.0.0"


def _get_user_agent() -> str:
    """Get the User-Agent string for HTTP requests.
    Returns
    -------
    str
        The User-Agent string including SDK version.
    """
    sdk_version = _get_sdk_version()
    return f"SnorkelAI-SDK/{sdk_version}"


def validate_arguments(*args: tuple, **kwargs: dict) -> None:
    DEPRECATED_ENVVARS: Set[str] = set()
    DEPRECATED_ARGS: Set[str] = set()
    if len(args) > 0:
        raise TypeError(f"got unexpected positional argument: {args}")
    extra_kwargs = set(kwargs.keys()) - DEPRECATED_ARGS
    if extra_kwargs:
        raise TypeError(f"got an unexpected keyword argument: {extra_kwargs}")
    deprecated_kwargs = set(kwargs.keys()) & DEPRECATED_ARGS
    if deprecated_kwargs:
        message = f"ignoring deprecated arguments: {deprecated_kwargs}"
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)
    deprecated_envvars = set(os.environ.keys()) & DEPRECATED_ENVVARS
    if deprecated_envvars:
        message = f"ignoring deprecated envvars: {deprecated_envvars}"
        warnings.warn(message, category=DeprecationWarning, stacklevel=2)
