from typing import Any, Dict, List, Optional, Union

from snorkelai.sdk.client_v3.tdm.api.fm_integrations import (
    get_fm_provider_status_fm_integrations__provider__status_get,
    list_integrations_fm_integrations_put,
)
from snorkelai.sdk.client_v3.tdm.api.secrets import (
    delete_secret_secrets_delete,
    list_secret_keys_secrets_put,
    set_secret_secrets_post,
)
from snorkelai.sdk.client_v3.tdm.models import (
    DeleteSecretParams,
    DeleteSecretParamsKwargs,
    ListIntegrationsParams,
    ListIntegrationsParamsKwargs,
    ListSecretParams,
    ListSecretParamsKwargs,
    SetSecretParams,
    SetSecretParamsKwargs,
    SetSecretParamsValueType1,
)
from snorkelai.sdk.client_v3.tdm.models.external_llm_provider import ExternalLLMProvider
from snorkelai.sdk.client_v3.utils import (
    DEFAULT_WORKSPACE_UID,
    _create_params_instance_or_unset_from_metadata,
    get_workspace_uid,
)
from snorkelai.sdk.context.ctx import SnorkelSDKContext
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("SDK")


def set_secret(
    key: str,
    value: Union[str, Dict[str, str]],
    secret_store: str = "local_store",
    kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """Adds secret to the secret store (Only for superadmin users).

    Parameters
    ----------
    key
        Key to reference the secret in the store
    value
        The secret being added
    secret_store
        The secret store to add the secret (only `local_store` supported now)
    kwargs
        Other connection kwargs for accesing the secret store

    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)
    input_value: Union[str, SetSecretParamsValueType1]
    if isinstance(value, dict):
        input_value = SetSecretParamsValueType1.from_dict(value)
    else:
        input_value = str(value)
    params = SetSecretParams(
        key=key,
        value=input_value,
        secret_store=secret_store,
        workspace_uid=workspace_uid,
        kwargs=_create_params_instance_or_unset_from_metadata(
            SetSecretParamsKwargs, kwargs
        ),
    )
    set_secret_secrets_post(body=params)
    logger.info(f"Added secret {key} to the secret store")


def list_secrets(
    secret_store: str = "local_store",
    workspace_uid: int = DEFAULT_WORKSPACE_UID,
    kwargs: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Gets all secret keys in a workspace (Only for superadmin users).

    Parameters
    ----------
    secret_store
        The secret store to list the secret (only `local_store` supported now)
    workspace_uid
        The workspace uid for the secret
    kwargs
        Other connection kwargs for accesing the secret store

    Returns
    -------
    List[str]
        All secret keys associated with a workspace

    """
    params = ListSecretParams(
        secret_store=secret_store,
        workspace_uid=workspace_uid,
        kwargs=_create_params_instance_or_unset_from_metadata(
            ListSecretParamsKwargs, kwargs
        ),
    )
    # Change this
    response = list_secret_keys_secrets_put(body=params)
    return response.keys


def delete_secret(
    key: str,
    secret_store: str = "local_store",
    workspace_uid: int = DEFAULT_WORKSPACE_UID,
    kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """Deletes a secret from the secret store (Only for superadmin users).

    Parameters
    ----------
    key
        Key to reference the secret in the store
    secret_store
        The secret store to delete the secret (only `local_store` supported now)
    workspace_uid
        The workspace uid for the secret
    kwargs
        Other connection kwargs for accesing the secret store

    """
    params = DeleteSecretParams(
        key=key,
        secret_store=secret_store,
        workspace_uid=workspace_uid,
        kwargs=_create_params_instance_or_unset_from_metadata(
            DeleteSecretParamsKwargs, kwargs
        ),
    )
    delete_secret_secrets_delete(body=params)
    logger.info(f"Deleted secret {key} from the secret store")


def list_integrations(
    secret_store: str = "local_store",
    workspace_uid: int = DEFAULT_WORKSPACE_UID,
    kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """Gets configuration status for each foundation model provider (Only for superadmin users).

    Parameters
    ----------
    secret_store
        The secret store to list the secret (only `local_store` supported now)
    workspace_uid
        The workspace uid for the secret
    kwargs
        Other connection kwargs for accesing the secret store

    """
    params = ListIntegrationsParams(
        secret_store=secret_store,
        workspace_uid=workspace_uid,
        kwargs=_create_params_instance_or_unset_from_metadata(
            ListIntegrationsParamsKwargs, kwargs
        ),
    )
    response = list_integrations_fm_integrations_put(body=params)
    return response["integrations"]


def get_model_provider_status(model_provider: ExternalLLMProvider) -> Dict[str, Any]:
    """Gets the status of a model provider.

    Parameters
    ----------
    model_provider
        The model provider to retrieve the status for

    Returns
    -------
    Dict[str, Any]
        The status of the model provider

    """
    response = get_fm_provider_status_fm_integrations__provider__status_get(
        provider=model_provider, workspace_uid=DEFAULT_WORKSPACE_UID
    )
    return response.to_dict()
