import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil import parser
from requests import HTTPError

from snorkelai.sdk.client_v3.fm_type import FMType
from snorkelai.sdk.client_v3.tdm.api.external_llm_configs import (
    add_external_llm_config_external_llm_configs_post,
    delete_external_llm_config_external_llm_configs__external_llm_config_uid__delete,
    get_external_llm_config_external_llm_configs__external_llm_config_uid__get,
    get_external_llm_configs_external_llm_configs_get,
    update_external_llm_config_external_llm_configs__external_llm_config_uid__put,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AddExternalLLMConfigPayload,
    AddExternalLLMConfigPayloadConfig,
    ExternalLLMConfig,
    UpdateExternalLLMConfigPayload,
    UpdateExternalLLMConfigPayloadConfig,
)
from snorkelai.sdk.client_v3.tdm.models.external_llm_provider import ExternalLLMProvider
from snorkelai.sdk.client_v3.tdm.types import Unset
from snorkelai.sdk.client_v3.utils import DEFAULT_WORKSPACE_UID


def _external_llm_configs_to_endpoint_dict(
    external_llm_configs: List[ExternalLLMConfig],
) -> Dict[str, str]:
    """Helper function to convert the backend response to a map from model name to endpoint"""
    endpoint_dict: Dict[str, str] = {}
    for external_llm_config in external_llm_configs:
        if isinstance(external_llm_config.config, Unset):
            endpoint_dict[external_llm_config.model_name] = ""
        else:
            model_parameters = external_llm_config.config.to_dict()
            if "endpoint_url" in model_parameters:
                endpoint_dict[external_llm_config.model_name] = model_parameters[
                    "endpoint_url"
                ]
            else:
                endpoint_dict[external_llm_config.model_name] = ""
    return endpoint_dict


def _get_detail_for_external_llm_config(
    external_llm_config: ExternalLLMConfig,
) -> Dict[str, Any]:
    """Helper function to get the detailed information for an external LLM Config"""
    if isinstance(external_llm_config.config, Unset):
        model_parameters = {}
    else:
        model_parameters = external_llm_config.config.to_dict()
    if "endpoint_url" in model_parameters:
        endpoint_url = model_parameters.pop("endpoint_url")
    else:
        endpoint_url = None
    if "fm_type" in model_parameters:
        fm_type = model_parameters.pop("fm_type")
    else:
        fm_type = None
    if isinstance(external_llm_config.created_at, Unset):
        created_at = ""
    else:
        created_at = external_llm_config.created_at.isoformat()
    return {
        "model_provider": external_llm_config.model_provider,
        "workspace_uid": external_llm_config.workspace_uid,
        "endpoint_url": endpoint_url,
        "fm_type": fm_type,
        "created": _get_readable_time_ago(created_at),
        "model_parameters": model_parameters,
    }


def _get_uid_for_model_name(model_name: str, workspace_uid: int) -> int:
    """Helper function to get an External LLM Config UID for a given model name and workspace uid"""
    external_llm_configs = get_external_llm_configs_external_llm_configs_get(
        workspace_uid=workspace_uid
    ).external_llm_configs
    uids_for_model_name = [
        external_llm_config.external_llm_config_uid
        for external_llm_config in external_llm_configs
        if external_llm_config.model_name == model_name
    ]
    if len(uids_for_model_name) != 1:
        raise ValueError(
            f"Expected exactly one external model endpoint for model name {model_name}, found {len(uids_for_model_name)}"
        )
    model_uid = uids_for_model_name[0]
    if isinstance(model_uid, Unset):
        raise ValueError(f"Mssing model UID for model name {model_name}")
    return model_uid


def _get_readable_time_ago(datetime_string: str) -> str:
    """Helper function to get the human readable time ago from a datetime string"""
    time_difference = datetime.now() - parser.parse(datetime_string)
    days = time_difference.days
    total_seconds = time_difference.seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    human_readable_parts = [
        f"{days} days" if days else "",
        f"{hours} hours" if hours else "",
        f"{minutes} minutes" if minutes else "",
        f"{seconds} seconds" if seconds else "",
    ]

    return ", ".join(part for part in human_readable_parts if part) + " ago"


def get_external_model_endpoints(
    model_name: Optional[str] = None, detail: bool = False
) -> Dict[str, Any]:
    """Gets the external model endpoints from DB (Only for superadmin users).

    Parameters
    ----------
    model_name
        Name of the model to retrieve the endpoint or configuration for. Defaults to None to return specified information for all models.
    detail
        Whether to return the full configuration for each model. Defaults to False to return only the endpoint URL.

    Returns
    -------
    Dict[str, Any]
        Mapping of model name to model configuration

    """
    if model_name is None:
        external_llm_configs = get_external_llm_configs_external_llm_configs_get(
            workspace_uid=DEFAULT_WORKSPACE_UID
        ).external_llm_configs
    else:
        uid = _get_uid_for_model_name(model_name, DEFAULT_WORKSPACE_UID)
        external_llm_configs = [
            get_external_llm_config_external_llm_configs__external_llm_config_uid__get(
                uid, workspace_uid=DEFAULT_WORKSPACE_UID
            )
        ]

    if detail:
        return {
            external_llm_config.model_name: _get_detail_for_external_llm_config(
                external_llm_config
            )
            for external_llm_config in external_llm_configs
        }
    else:
        return _external_llm_configs_to_endpoint_dict(
            external_llm_configs=external_llm_configs
        )


def set_external_model_endpoint(
    model_name: str,
    endpoint: str,
    model_provider: str,
    fm_type: str,
    **config_kwargs: Any,
) -> None:
    """Adds an external model endpoint to DB (Only for superadmin users).
    NOTE: this will impact all users who elect to use `model_name`

    Parameters
    ----------
    model_name
        Name of the model
    endpoint
        Endpoint of the model
    model_provider
        Name of the model provider (one of: azure_ml, azure_openai, bedrock, custom_inference_service, huggingface, openai, vertexai_lm)
    fm_type
        The model type of the foundation mode (one of: text2text, qa, docvqa)
    config_kwargs
        Any additional config options to set for the model

    """
    # Validating endpoint
    if not re.search(r"^https?://", endpoint):
        raise ValueError(f"Endpoint {endpoint} must follow 'http(s)://' format")

    if fm_type not in {item.value for item in FMType}:
        raise ValueError(
            f"{fm_type} is not a valid {FMType.__name__}. Supported values are {FMType.__members__.keys()}"
        )

    config_to_use: Dict[str, Any] = {
        "endpoint_url": endpoint,
        "fm_type": fm_type,
        **config_kwargs,
    }

    try:
        # Try to add first
        payload = AddExternalLLMConfigPayload(
            model_name=model_name,
            model_provider=ExternalLLMProvider(model_provider),
            config=AddExternalLLMConfigPayloadConfig.from_dict(config_to_use),
            workspace_uid=DEFAULT_WORKSPACE_UID,
        )

        add_external_llm_config_external_llm_configs_post(body=payload)
    except HTTPError as e:
        if e.response and e.response.status_code == 400:
            # If already exists, update instead
            uid = _get_uid_for_model_name(model_name, DEFAULT_WORKSPACE_UID)
            update_external_llm_config_external_llm_configs__external_llm_config_uid__put(
                uid,
                body=UpdateExternalLLMConfigPayload(
                    config=UpdateExternalLLMConfigPayloadConfig.from_dict(config_to_use)
                ),
                workspace_uid=DEFAULT_WORKSPACE_UID,
            )

        else:
            raise e


def delete_external_model_endpoint(model_name: str) -> None:
    """Removes an external model endpoint from DB (Only for superadmin users).

    Parameters
    ----------
    model_name
        Name of the model

    """
    uid = _get_uid_for_model_name(model_name, DEFAULT_WORKSPACE_UID)
    delete_external_llm_config_external_llm_configs__external_llm_config_uid__delete(
        uid, workspace_uid=DEFAULT_WORKSPACE_UID
    )
