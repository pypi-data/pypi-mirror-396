import json
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from requests.exceptions import HTTPError

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    fetch_dataset_by_uid_datasets__dataset_uid__get,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    get_datasets as get_datasets_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.jobs import (
    cancel_job_jobs__job_uid__cancel_post,
    get_job_for_uid_jobs__job_uid__get,
)
from snorkelai.sdk.client_v3.tdm.api.sources import get_sources_sources_get
from snorkelai.sdk.client_v3.tdm.api.workspace import (
    get_workspace_workspaces__workspace_uid__get,
    list_workspaces_workspaces_get,
)
from snorkelai.sdk.client_v3.tdm.models.job_info import JobInfo
from snorkelai.sdk.client_v3.tdm.types import UNSET, Unset
from snorkelai.sdk.types.jobs import JobState
from snorkelai.sdk.types.splits import Splits
from snorkelai.sdk.utils.logging import DEFAULT_SERVER_ERROR_MESSAGE, get_logger

SPLITS = [split.value for split in Splits]
DEFAULT_TUNING_SPLITS = ["train", "dev", "valid"]
NodeType = Union[str, int]
IdType = Union[str, int]
IdTypeList = Union[List[str], List[int]]
T = TypeVar("T")
U = TypeVar("U")
DEFAULT_WORKSPACE_UID = 1
# Constants for LabelSpaces so we don't have to import /label_spaces.
SINGLE_LABEL_SPACE = "SingleLabelSpace"
MULTI_LABEL_SPACE = "MultiLabelSpace"
SEQUENCE_LABEL_SPACE = "SequenceLabelSpace"
WORD_LABEL_SPACE = "WordLabelSpace"


logger = get_logger("SDK")


class JobFailedException(Exception):
    pass


class JobCancelledException(Exception):
    pass


class JobTimedOutException(Exception):
    pass


class OperatorNotFound(Exception):
    pass


def require_api_key(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        ctx = SnorkelSDKContext.get_global() if args else None
        if ctx and ctx.tdm_client.api_key is None:
            raise RuntimeError("Valid API key is required for this method.")
        return f(*args, **kwargs)

    return decorated_function


def _get_job_error_message(response: JobInfo) -> str:
    if (
        response.message == DEFAULT_SERVER_ERROR_MESSAGE
        and response.detail
        and "exception_type" in response.detail.to_dict()
        and "exception_detail" in response.detail.to_dict()
    ):
        return f"{response.detail['exception_type']}: {response.detail['exception_detail']}"
    return response.message or ""


def get_job_debug_error_message(response: JobInfo) -> str:
    err_msg_dict = dict(
        message=response.message,
        # contains job failure traceback
        detail=response.detail.to_dict() if response.detail else None,
    )
    return json.dumps(err_msg_dict)


def poll_job_status(
    job_id: str, timeout: Optional[timedelta] = None, verbose: bool = True
) -> Dict[str, Any]:
    """Poll /jobs endpoint and print statuses.

    Parameters
    ----------
    job_id
        UID of the job
    timeout
        Optional polling timeout duration, jobs that exceed the timeout will be canceled
    verbose
        Optional argument to increase verbosity of the output logs

    Returns
    -------
    Dict[str, Any]
        Final job status response if job completes

    Raises
    ------
    JobFailedException
        If job fails
    JobCancelledException
        If job is cancelled by user

    Examples
    --------
    .. doctest::

        >>> sai.poll_job_status(job_id)
        {
            'uid': <job_id>,
            'job_type': <job_type>,
            'state': <state>, # completed or failed
            'enqueued_time': <timestamp>,
            'execution_start_time': <timestamp>,
            'end_time': <timestamp>,
            'application_uid':<application_uid>,
            'dataset_uid': <dataset_uid>,
            'node_uid': <node_uid>,
            'user_uid':<user_uid>,
            'workspace_uid': <workspace_uid>,
            'percent': <percent>, # Based on state
            'message':  <message>,
            'detail': <detail>,
            'pod_name':  <pod_name>,
            'function_name':  <function_name>,
            'process_id':  <process_id>,
            'timing': <timing_dict>
        }

    """
    ctx = SnorkelSDKContext.get_global()
    complete = False
    last_message = None
    last_print_time = start_time = datetime.now()
    while not complete and (timeout is None or datetime.now() - start_time < timeout):
        try:
            response = get_job_for_uid_jobs__job_uid__get(job_uid=job_id)
            if response.state == JobState.FAILED:
                error_msg = (
                    get_job_debug_error_message(response)
                    if ctx.debug
                    else _get_job_error_message(response)
                )
                raise JobFailedException(error_msg)
            if response.state == JobState.CANCELLED:
                raise JobCancelledException(response.message)
            new_message = response.message
            if (
                last_message != new_message
                or datetime.now() - last_print_time > timedelta(seconds=10)
            ):
                time_since = datetime.now() - start_time
                progress = response.percent
                if verbose:
                    progress_str = f"({progress}%) " if progress is not None else ""
                    print(
                        f"+{time_since.total_seconds():.2f}s {progress_str}{new_message}",
                        flush=True,
                    )
                last_print_time = datetime.now()
            last_message = new_message
            complete = response.state == JobState.COMPLETED
        except HTTPError as e:
            # Ignore Bad Gateway/Gateway Timeout errors
            if e.response.status_code not in {502, 504}:
                raise e
        # Polling a job status is cheap so we do it every 100ms to avoid unnecesary
        # delays for fast jobs.
        poll_wait_secs = 0.1
        time.sleep(poll_wait_secs)
    if not complete:
        logger.warning(f"Job {job_id} timed out after {timeout}. Canceling")
        cancel_job_jobs__job_uid__cancel_post(job_uid=job_id)
        raise JobTimedOutException()
    return response.to_dict()


class DatasetMetadata(NamedTuple):
    name: str
    uid: int
    mta_enabled: bool


def get_dataset_metadata(dataset: IdType) -> DatasetMetadata:
    """Fetch the metadata of a dataset by name or UID.

    This is the recommended entrypoint for retrieving generic dataset metadata, as it
    automatically handles the case where the dataset is specified by name
    or UID, and adds error handling.

    If additional properties are needed, add them to DatasetMetadata and
    update the function accordingly.

    Parameters
    ----------
    dataset
        Name or UID of the dataset

    Returns
    -------
    DatasetMetadata
        Metadata of the dataset

    Raises
    ------
    ValueError
        If the dataset doesn't exist.

    """

    def _res_to_metadata(res: Dict[str, Any]) -> DatasetMetadata:
        return DatasetMetadata(
            name=res["name"],
            uid=res["dataset_uid"],
            mta_enabled=res["metadata"].get("enable_mta", False),
        )

    workspace_name = SnorkelSDKContext.get_global().workspace_name
    if isinstance(dataset, str):
        try:
            workspace_uid = get_workspace_uid(workspace_name)
            datasets_res = get_datasets_autogen(
                name=dataset, workspace_uid=_wrap_in_unset(workspace_uid)
            )
            if len(datasets_res) == 1:
                return _res_to_metadata(datasets_res[0].to_dict())
            else:
                raise ValueError(
                    f"Dataset with name '{dataset}' not found in workspace {workspace_name}."
                )
        except ValueError as e:
            if "Please specify a workspace" in str(e):
                raise ValueError(
                    str(e).replace(
                        "specify a workspace",
                        "specify a workspace or provide the UID of the dataset",
                    )
                ) from e
            raise e
    else:
        try:
            dataset_res = fetch_dataset_by_uid_datasets__dataset_uid__get(dataset)
            return _res_to_metadata(dataset_res.to_dict())
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Dataset with UID: '{dataset}' not found.") from e
            raise e


def get_dataset_uid(dataset: IdType) -> int:
    """Fetch the UID of a dataset by name or UID

    Parameters
    ----------
    dataset
        Name or UID of the dataset

    Returns
    -------
    int
        UID of the dataset

    Raises
    ------
    ValueError
        If a dataset doesn't exist.

    """
    return get_dataset_metadata(dataset).uid


def get_dataset_name(dataset_uid: int) -> str:
    """Fetch the UID of a Dataset by name

    Parameters
    ----------
    dataset_uid
        UID of the dataset

    Returns
    -------
    str
        Name of the dataset

    """
    return get_dataset_metadata(dataset_uid).name


def get_workspace_uid(workspace_name: str) -> int:
    """Fetch the UID of a Workspace by name

    Parameters
    ----------
    workspace_name
        Name of the workspace

    Returns
    -------
    int
        UID of the workspace

    """
    response = list_workspaces_workspaces_get(workspace_name=workspace_name)
    if len(response.workspaces) != 1:
        raise ValueError(f"Workspace with name '{workspace_name}' not found")
    workspace = response.workspaces[0]
    if isinstance(workspace.workspace_uid, Unset):
        raise ValueError(f"Workspace with name '{workspace_name}' has no UID")
    return workspace.workspace_uid


def get_workspace_name(workspace_uid: int) -> str:
    """Fetch the name of a Workspace by UID

    Parameters
    ----------
    workspace_uid
        UID of the workspace

    Returns
    -------
    str
        Name of the workspace

    """
    workspace = get_workspace_workspaces__workspace_uid__get(
        workspace_uid=workspace_uid
    )
    return workspace.workspace.name


def get_source_uid(source_name: str) -> int:
    """Translate a source_name to a source_uid.

    Parameters
    ----------
    source_name
        A valid source name

    Returns
    -------
    int
        The source_uid for source_name

    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)
    sources = get_sources_sources_get(
        workspace_uid=_wrap_in_unset(workspace_uid)
    ).sources
    source_uids = []
    for source in sources:
        if source.source_name == source_name:
            source_uids.append(int(source.source_uid))

    if len(source_uids) == 0:
        raise ValueError(f"No source UID found for {source_name}")
    return source_uids[0]


def check_split_exists(datasources: List[Dict[str, Any]], split: str) -> None:
    if split not in SPLITS:
        raise ValueError(f"Invalid split name: {split}. Expected one of {SPLITS}")
    # Remember that "dev" doesn't have its own datasources. The individual examples
    # in "train" datasources are split into "train" and "dev" splits.
    load_split = "train" if split == "dev" else split
    if load_split not in {ds["split"] for ds in datasources}:
        raise RuntimeError(f"Split {split} does not exist")


def arraylike_to_list(x: Optional[Union[List[Any], np.ndarray]]) -> Optional[List[Any]]:
    if x is None:
        return None

    if isinstance(x, np.ndarray):
        x = x.tolist()

    if isinstance(x, tuple):
        x = list(x)

    if not isinstance(x, list):  # scalar
        x = [x]

    return x


def _wrap_in_unset(some_obj: Optional[T]) -> Union[T, Unset]:
    """This function is pure syntactic sugar, for using auto-generated code for tdm client within SF SDK 2.0
    It should not be exposed to public API
    """
    if some_obj is None:
        return UNSET
    return some_obj


def _unwrap_unset(value: Union[T, Unset], default: T) -> T:
    """This function is pure syntactic sugar, for using auto-generated code for tdm client within SF SDK 2.0
    It should not be exposed to public API
    """
    return default if value is UNSET else cast(T, value)


def _create_params_instance_or_unset_from_metadata(
    class_handle: Type[U], metadata: Optional[Dict[str, Any]]
) -> Union[Unset, U]:
    """This function is pure syntactic sugar, for using auto-generated code for tdm client within SF SDK 2.0
    It should not be exposed to public API
    """
    if metadata is None:
        return UNSET

    ret = class_handle()
    if hasattr(ret, "additional_properties"):
        setattr(ret, "additional_properties", metadata)  # noqa: B010
    else:
        raise AttributeError(
            f"{str(class_handle)}.additional_properties does not exist, as data member, can't be set to {metadata}"
        )
    return ret
