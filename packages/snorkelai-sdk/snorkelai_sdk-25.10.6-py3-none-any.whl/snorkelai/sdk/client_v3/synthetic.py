from typing import Any, List, Optional, Union

import pandas as pd

from snorkelai.sdk.client_v3.fm_suite import _prompt_fm, prompt_fm
from snorkelai.sdk.client_v3.tdm.api.fm_prompting import AugmentDatasetRequest
from snorkelai.sdk.client_v3.tdm.models.augment_dataset_request_fm_hyperparameters import (
    AugmentDatasetRequestFmHyperparameters,
)
from snorkelai.sdk.client_v3.tdm.models.llm_type import LLMType
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import IdType, get_workspace_uid
from snorkelai.sdk.context.ctx import SnorkelSDKContext

TEXT_FIELD = "text"


def augment_data(
    data: Union[List[str], str],
    model_name: str,
    runs_per_prompt: int = 1,
    prompt: str = "Rewrite the following text whilst retaining the core meaning.",
    sync: bool = True,
    **fm_hyperparameters: Any,
) -> Union[pd.DataFrame, str]:
    """Augment each row of the data by the number of times specified and return a
    dataframe with the synthetic data as an additional column.

    Parameters
    ----------
    data
        The data to augment.
    model_name
        The name of the foundation model to use.
    runs_per_prompt
        The number of times to augment each row.
    prompt
        The prompt prefix to send to the foundation model together with each
        row.
    sync
        Whether to wait for the job to complete before returning the result.
    fm_hyperparameters
        Additional keyword arguments to pass to the foundation model such as
        temperature, max_tokens, etc.

    Returns
    -------
    df
        Dataframe containing the augmentations for the data points.
    job_id
        The job id of the augment data job which can be used to monitor progress
        with sai.poll_job_status(job_id).

    Examples
    --------
    >>> sai.augment_data(["hello, how can I help you?", "sorry that is not possible"], "openai/gpt-4")
       | text                           | generated_text                              | perplexity
    --------------------------------------------------------------------------------------------------------------
    0  | hello, how can I help you?     | welcome, ask me a question to get started   | 0.0113636364
    1  | sorry that is not possible     | unfortunately you cannot do that            | 0.8901232123

    >>> sai.augment_data(["hello, how can I help you?", "sorry that is not possible"], "openai/gpt-4", runs_per_prompt=2)
       | text                           | generated_text                              | perplexity
    --------------------------------------------------------------------------------------------------------------
    0  | hello, how can I help you?     | welcome, ask me a question to get started   | 0.0113636364
    1  | sorry that is not possible     | unfortunately you cannot do that            | 0.8901232123
    0  | hello, how can I help you?     | Let me know how to get started.             | 0.2313232442
    1  | sorry that is not possible     | bad luck, you cannot do that.               | 0.8313232442

    """
    single_row = not isinstance(data, list)
    _data = [data] if single_row else data
    # Add prompt prefix to each row
    prompts = [f"{prompt}\n{row}" for row in _data]
    rsp = prompt_fm(
        prompts,
        model_name,
        LLMType.TEXT2TEXT,
        sync=sync,
        runs_per_prompt=runs_per_prompt,
        **fm_hyperparameters,
    )
    if sync:
        assert isinstance(rsp, pd.DataFrame)  # mypy
        # remove prompt prefix
        rsp[TEXT_FIELD] = rsp[TEXT_FIELD].apply(lambda x: x[len(prompt) + 1 :])
    return rsp


def augment_dataset(
    dataset: IdType,
    x_uids: List[str],
    model_name: str,
    runs_per_prompt: int = 1,
    prompt: str = "Your task is to rewrite the a set of text fields whilst retaining the core meaning. You should keep the same language and ensure each re-written field is of a similar length to the original.",
    fields: Optional[List[str]] = None,
    sync: bool = True,
    **fm_hyperparameters: Any,
) -> Union[pd.DataFrame, str]:
    """Augment each row of the dataset by the number of times specified and return
    a dataframe containing only the synthetic data. By default, all fields are
    augmented and the foundation model performs the augmentation of each row
    (all fields) in one inference step.

    Parameters
    ----------
    dataset
        The name or UID of the dataset to generate a synthetic augmentation of.
    x_uids
        The x_uids within the dataset to augment.
    model_name
        The name of the foundation model to use.
    runs_per_prompt
        The number of times to augment each row.
    prompt
        The prompt passed to the foundation model for each row. Note that by
        default, the prompt is appended with the fields to make the following:
        "Rewrite the following text fields whilst retaining the core meaning. You should keep the same language and ensure each re-written field is of a similar length to the original.
        Return your answer in a json format with the same keys as the fields: [field_1, field_2, ...]
        Here is the data you have to rewrite...".
        To override this default behavior, simply pass at least one field
        wrapped in parentheses, e.g. {field_1}, within the prompt and no
        additional text will be append to the prompt.
    fields
        The fields to augment. If not provided, all fields will be augmented.
    sync
        Whether to wait for the job to complete before returning the result.
    fm_hyperparameters
        Additional keyword arguments to pass to the foundation model such as
        temperature, max_tokens, etc.

    Returns
    -------
    df
        Dataframe containing the augmentations for the data points.
    job_id
        The job id of the augment data job which can be used to monitor progress
        with sai.poll_job_status(job_id).

    Examples
    --------
    >>> sai.augment_dataset(dataset=1, x_uids=["0", "1"], model_name="openai/gpt-4", runs_per_prompt=2)
       | subject                                | body                                                                    | perplexity
    -----------------------------------------------------------------------------------------------------------------------------------
    0  | Fill in survey for $50 amazon voucher  | The email is asking you to fill in a survey for an amazon voucher       | 0.891
    1  | Hey it's Bob, free on Sat?             | The email is from your friend Bob asking if you're free on Saturday     | 0.787
    0  | Free survey for $50                    | Want a free $50 amazon voucher? Fill in our survey.                     | 0.911
    1  | No Plans on Sat, Bob?                  | Let's meet up on Sat. Bob.                                              | 0.991

    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)
    request_params = AugmentDatasetRequest(
        x_uids=x_uids,
        model_name=model_name,
        num_runs=runs_per_prompt,
        prompt=prompt,
        fields=fields or UNSET,
        fm_hyperparameters=AugmentDatasetRequestFmHyperparameters.from_dict(
            fm_hyperparameters
        ),
        workspace_uid=workspace_uid,
    )
    return _prompt_fm(request_params, sync, dataset)
