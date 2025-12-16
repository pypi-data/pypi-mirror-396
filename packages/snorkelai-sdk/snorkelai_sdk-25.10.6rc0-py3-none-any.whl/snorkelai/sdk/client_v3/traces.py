from typing import Any, Dict

from snorkelai.sdk.client_v3.tdm.api.traces import (
    validate_dataset_traces_trace_validate_post,
)
from snorkelai.sdk.client_v3.tdm.models.body_validate_dataset_traces_trace_validate_post import (
    BodyValidateDatasetTracesTraceValidatePost,
)
from snorkelai.sdk.client_v3.tdm.types import File
from snorkelai.sdk.context.ctx import SnorkelSDKContext, _get_workspace_uid


def validate_traces(trace_csv_file_path: str, trace_column: str) -> Dict[str, Any]:
    """Validate the traces in the trace CSV file.

    Parameters
    ----------
    trace_csv_file_path
        The path to the trace CSV file.
    trace_column
        The column name containing the trace JSON data.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the validation results.
    """
    try:
        ctx = SnorkelSDKContext.get_global()
    except AttributeError:
        raise ValueError("No SnorkelSDKContext found") from None

    workspace_uid = _get_workspace_uid(ctx.tdm_client, ctx.workspace_name)

    with open(trace_csv_file_path, "rb") as f:
        file = File(payload=f, file_name=trace_csv_file_path, mime_type="text/csv")
        body = BodyValidateDatasetTracesTraceValidatePost(file=file)

        response = validate_dataset_traces_trace_validate_post(
            body=body,
            trace_column=trace_column,
            workspace_uid=workspace_uid,
        )
        return response.to_dict()
