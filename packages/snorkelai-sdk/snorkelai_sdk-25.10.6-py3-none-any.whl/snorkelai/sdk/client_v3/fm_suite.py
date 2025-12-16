from typing import Any, List, Optional, Union

import pandas as pd

from snorkelai.sdk.client_v3.tdm.api.fm_prompting import (
    augment_dataset_augment_dataset__dataset_uid__post,
    prompt_fm_over_dataset_prompt_fm__dataset_uid__post,
    prompt_fm_over_dataset_results_prompt_fm_responses_post,
    prompt_fm_prompt_fm_post,
)
from snorkelai.sdk.client_v3.tdm.models.augment_dataset_request import (
    AugmentDatasetRequest,
)
from snorkelai.sdk.client_v3.tdm.models.llm_type import LLMType
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_dataset_request import (
    PromptFMDatasetRequest,
)
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_dataset_request_cacher_kwargs import (
    PromptFMDatasetRequestCacherKwargs,
)
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_dataset_request_fm_hyperparameters import (
    PromptFMDatasetRequestFmHyperparameters,
)
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_request import PromptFMRequest
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_request_cacher_kwargs import (
    PromptFMRequestCacherKwargs,
)
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_request_fm_hyperparameters import (
    PromptFMRequestFmHyperparameters,
)
from snorkelai.sdk.client_v3.tdm.models.prompt_fm_response import PromptFMResponse
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import (
    IdType,
    get_dataset_uid,
    poll_job_status,
)
from snorkelai.sdk.context.constants import DEFAULT_WORKSPACE_UID
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("SDK")


DATAPOINT_UID_FIELD = "__DATAPOINT_UID"


def prompt_fm(
    prompt: Union[str, List[str]],
    model_name: str,
    model_type: Optional[LLMType] = None,
    question: Optional[str] = None,
    runs_per_prompt: int = 1,
    sync: bool = True,
    cache_name: str = "default",
    **fm_hyperparameters: Any,
) -> Union[pd.DataFrame, str]:
    """Send one or more prompts to a foundation model

    Parameters
    ----------
    prompt
        The prompt(s) to send to the foundation model.
    model_name
        The name of the foundation model to use.
    model_type
        The way we should use the foundation model, must be one of the LLMType
        values.
    question
        When provided, this get's passed to the model for each prompt which is
        useful for information retrieval tasks. The prompt argument essentially
        then becomes the context(s) which contains the answer to the question.
    runs_per_prompt
        The number of times to run a prompt, note each response can be
        different. All will be cached.
    sync
        Whether to wait for the job to complete before returning the result.
    cache_name
        The cache name is used in the hash construction. To run a prompt and get
        a different result, you should change the cache name to something that
        hasn't been used before.
        For example:
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o")
        The meaning of life is to work...
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o") << hit's the cache
        The meaning of life is to work...
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o", cache_name="run_2") << hit's a different part of the cache
        The meaning of life is to have fun!
    fm_hyperparameters
        Additional keyword arguments to pass to the foundation model such as
        temperature, max_tokens, etc.

    Returns
    -------
    df
        Dataframe containing the predictions for the data points. There are two
        columns, the input prompt and the output of the foundation model.
    job_id
        The job id of the prompt inference job which can be used to monitor
        progress with sai.poll_job_status(job_id).

    Examples
    --------
    >>> sai.prompt_fm(prompt="What is the meaning of life?", model_name="openai/gpt-4")
       | text                           | generated_text                      | perplexity
    --------------------------------------------------------------------------------------------------------------
    0  | What is the meaning of life?   | Life is all about having fun!       | 0.789


    >>> sai.prompt_fm(prompt=["What is the meaning of life?", "What is the meaning of death?"], model_name="openai/gpt-4")
       | text                           | generated_text                      | perplexity
    --------------------------------------------------------------------------------------------------------------
    0  | What is the meaning of life?   | Life is all about having fun!       | 0.789
    1  | What is the meaning of death?  | Death is about not having fun!      | 0.981

    >>> sai.prompt_fm(question="What is surname", prompt="Joe Bloggs is a person", model_name="deepset/roberta-base-squad2")
       | text                           | answer         | start  | end   | score
    -------------------------------------------------------------------------------------------------------------
    0  | Joe Bloggs is a person         | Bloggs         | 4      | 11    | 0.985

    """
    single_prompt = not isinstance(prompt, list)
    prompts = [prompt] if single_prompt else prompt
    cache_info = {"sdk": cache_name}

    request_params = PromptFMRequest(
        model_name=model_name,
        input_data=prompts,  # type: ignore
        prompt_init_param=question or UNSET,
        model_type=LLMType(model_type) if model_type else UNSET,
        workspace_uid=DEFAULT_WORKSPACE_UID,
        use_cached_results=False,
        cacher_kwargs=PromptFMRequestCacherKwargs.from_dict({"cache_info": cache_info}),
        fm_hyperparameters=PromptFMRequestFmHyperparameters.from_dict(
            fm_hyperparameters
        ),
        num_runs=runs_per_prompt,
    )
    return _prompt_fm(request_params, sync)


def prompt_fm_over_dataset(
    prompt_template: str,
    dataset: IdType,
    x_uids: List[str],
    model_name: str,
    model_type: Optional[LLMType] = None,
    runs_per_prompt: int = 1,
    sync: bool = True,
    cache_name: str = "default",
    system_prompt: Optional[str] = None,
    **fm_hyperparameters: Any,
) -> Union[pd.DataFrame, str]:
    """Run a prompt over a dataset. Any field in the dataset can be referenced in
    the prompt by using curly braces, {field_name}.

    Parameters
    ----------
    prompt_template
        The prompt template used to format input rows sent to the foundation model.
    dataset
        The name or UID of the dataset containing the data we want to prompt over.
    x_uids
        The x_uids of the rows within the dataset to prompt over.
    model_name
        The name of the foundation model to use.
    model_type
        The way we should use the foundation model, must be one of the LLMType
        values.
    runs_per_prompt
        The number of times to run inference over an xuid, note each response
        can be different. All will be cached.
    sync
        Whether to wait for the job to complete before returning the result.
    cache_name
        The cache name is used in the hash construction. To run a prompt and get
        a different result, you should change the cache name to something that
        hasn't been used before.
        For example:
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o")
        The meaning of life is to work...
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o") << hit's the cache
        The meaning of life is to work...
        >> sai.prompt_fm("What is the meaning of life?", "openai/gpt-4o", cache_name="run_2") << hit's a different part of the cache
        The meaning of life is to have fun!
    system_prompt
        The system prompt to prepend to the prompt.
    fm_hyperparameters
        Additional keyword arguments to pass to the foundation model such as
        temperature, max_tokens, etc.

    Returns
    -------
    df
        Dataframe containing the predictions for the data points. There are two
        columns, the input prompt and the output of the foundation model.
    job_id
        The job id of the prompt inference job which can be used to monitor
        progress with sai.poll_job_status(job_id).

    Examples
    --------
    >>> sai.prompt_fm_over_dataset(prompt_template="{email_subject}. What is this email about?", dataset=1, x_uids=["0", "1"], model_name="openai/gpt-4")
       | email_subject                          | generated_text                                                          | perplexity
    -----------------------------------------------------------------------------------------------------------------------------------
    0  | Fill in survey for $50 amazon voucher  | The email is asking you to fill in a survey for an amazon voucher       | 0.891
    1  | Hey it's Bob, free on Sat?             | The email is from your friend Bob as if you're free on Saturday         | 0.787

    """
    dataset_uid = get_dataset_uid(dataset)
    cache_info = {"sdk": cache_name, "dataset_uid": dataset_uid}
    request_params = PromptFMDatasetRequest(
        x_uids=x_uids,
        model_name=model_name,
        prompt=prompt_template,
        model_type=LLMType(model_type) if model_type else UNSET,
        workspace_uid=DEFAULT_WORKSPACE_UID,
        use_cached_results=False,
        cacher_kwargs=PromptFMDatasetRequestCacherKwargs.from_dict(
            {"cache_info": cache_info}
        ),
        fm_hyperparameters=PromptFMDatasetRequestFmHyperparameters.from_dict(
            fm_hyperparameters
        ),
        num_runs=runs_per_prompt,
        system_prompt=system_prompt or UNSET,
    )
    return _prompt_fm(request_params, sync, dataset)


def _prompt_fm(
    request_params: Union[
        PromptFMRequest, PromptFMDatasetRequest, AugmentDatasetRequest
    ],
    sync: bool,
    dataset: Optional[IdType] = None,
) -> Union[pd.DataFrame, str]:
    if dataset is not None:
        dataset_uid = get_dataset_uid(dataset)
    # run inference in engine job
    if isinstance(request_params, PromptFMRequest):
        rsp = prompt_fm_prompt_fm_post(body=request_params)
    elif isinstance(request_params, PromptFMDatasetRequest):
        assert isinstance(dataset_uid, int)  # mypy
        rsp = prompt_fm_over_dataset_prompt_fm__dataset_uid__post(
            dataset_uid=dataset_uid, body=request_params
        )
    elif isinstance(request_params, AugmentDatasetRequest):
        assert isinstance(dataset_uid, int)  # mypy
        rsp = augment_dataset_augment_dataset__dataset_uid__post(
            dataset_uid=dataset_uid, body=request_params
        )
    else:
        raise ValueError(f"Invalid request type: {type(request_params)}")
    async_response = PromptFMResponse(**rsp.to_dict())
    job_id = async_response.job_id
    assert isinstance(job_id, str)  # mypy
    # if running async, return job_id
    if not sync:
        print(
            f"Note the job progress can always be monitored by running sai.poll_job_status('{job_id}')"
        )
        return job_id
    # if running sync, wait for job to complete
    poll_job_status(job_id)
    # get results by running job again, but this time hitting the cache
    request_params.use_cached_results = True
    if isinstance(request_params, PromptFMRequest):
        rsp = prompt_fm_prompt_fm_post(body=request_params)
    elif isinstance(request_params, PromptFMDatasetRequest):
        rsp = prompt_fm_over_dataset_results_prompt_fm_responses_post(
            body=request_params
        )
    elif isinstance(request_params, AugmentDatasetRequest):
        assert isinstance(dataset_uid, int)  # mypy
        rsp = augment_dataset_augment_dataset__dataset_uid__post(
            dataset_uid=dataset_uid, body=request_params
        )
    else:
        raise ValueError(f"Invalid request type: {type(request_params)}")
    sync_response = PromptFMResponse(**rsp.to_dict())
    data = sync_response.data
    assert isinstance(data, list)  # mypy
    df = pd.DataFrame(data)

    if DATAPOINT_UID_FIELD in df:
        df = df.set_index(DATAPOINT_UID_FIELD)
        df.index.name = None

    # handling multiple runs
    elif request_params.num_runs and request_params.num_runs > 1:
        df.index = pd.Index(
            list(range(len(df) // request_params.num_runs)) * request_params.num_runs
        )

    return df
