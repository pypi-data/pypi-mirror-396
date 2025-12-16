from typing import Any, Dict, List

from snorkelai.sdk.client_v3.tdm.api.connector_configs import (
    create_connector_config_v1_connector_configs_post,
    delete_connector_config_v1_connector_configs__config_uid__delete,
    get_config_permissions_v1_connector_configs__config_uid__permissions_get,
    get_connector_config_v1_connector_configs__config_uid__get,
    list_connector_configs_v1_connector_configs_get,
    update_connector_config_v1_connector_configs__config_uid__put,
)
from snorkelai.sdk.client_v3.tdm.models.data_connector import DataConnector
from snorkelai.sdk.client_v3.tdm.models.data_connector_config_creation_request import (
    DataConnectorConfigCreationRequest,
)
from snorkelai.sdk.client_v3.tdm.models.data_connector_config_creation_request_config import (
    DataConnectorConfigCreationRequestConfig,
)
from snorkelai.sdk.client_v3.tdm.models.update_config_request import UpdateConfigRequest
from snorkelai.sdk.client_v3.tdm.models.update_config_request_new_config import (
    UpdateConfigRequestNewConfig,
)
from snorkelai.sdk.client_v3.utils import get_workspace_uid
from snorkelai.sdk.context.ctx import SnorkelSDKContext


def list_connector_configs(connector_type: str) -> List[Dict[str, Any]]:
    """List all configurations for a specific connector type.

    Parameters
    ----------
    connector_type
        The type of connector to list configurations for (e.g. "AmazonS3")

    Returns
    -------
    List[Dict[str, Any]]
        A list of connector configurations of the given type

    Examples
    --------
    >>> from snorkelai.sdk.client import list_connector_configs
    >>> configs = list_connector_configs("AmazonS3")
    >>> print(configs)
    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    response = list_connector_configs_v1_connector_configs_get(
        type=connector_type, workspace_uid=workspace_uid
    )
    return [config.to_dict() for config in response]


def get_connector_config(config_uid: int) -> Dict[str, Any]:
    """Get a connector configuration by its UID.

    Parameters
    ----------
    config_uid
        The UID of the connector configuration to get

    Returns
    -------
    Dict[str, Any]
        A dictionary representing the connector configuration

    Examples
    --------
    >>> from snorkelai.sdk.client import get_connector_config
    >>> config = get_connector_config(123)
    >>> print(config)
    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    response = get_connector_config_v1_connector_configs__config_uid__get(
        config_uid=config_uid, workspace_uid=workspace_uid
    )
    permissions_response = (
        get_config_permissions_v1_connector_configs__config_uid__permissions_get(
            config_uid=config_uid, workspace_uid=workspace_uid
        )
    )
    return {
        "config": response.to_dict(),
        "permissions": permissions_response,
    }


def create_connector_config(
    name: str,
    connector_type: str,
    config: Dict[str, Any],
) -> int:
    """Create a new connector configuration.

    Parameters
    ----------
    name
        The name of the connector configuration
    connector_type
        The type of connector to create a configuration (e.g. "AmazonS3")
    config
        The connector configuration

    Returns
    -------
    int
        The UID of the created connector configuration

    Examples
    --------
    >>> from snorkelai.sdk.client import create_connector_config
    >>> config_uid = create_connector_config(
    ...     name="my_s3_config",
    ...     connector_type="AmazonS3",
    ...     config={
    ...         "access_key_id": "my_access_key_id",
    ...         "secret_access_key": "my_secret_access_key",
    ...         "region": "us-east-1",
    ...     },
    ... )
    >>> print(config_uid)
    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    config_obj = DataConnectorConfigCreationRequestConfig.from_dict(config)
    data_connector_type = DataConnector(connector_type)

    request = DataConnectorConfigCreationRequest(
        name=name,
        data_connector_type=data_connector_type,
        config=config_obj,
        workspace_uid=workspace_uid,
    )

    response = create_connector_config_v1_connector_configs_post(body=request)
    return response


def update_connector_config(
    config_uid: int,
    new_name: str,
    new_config: Dict[str, Any],
) -> None:
    """Update a connector configuration.

    Parameters
    ----------
    config_uid
        The UID of the connector configuration to update
    new_name
        The new name of the connector configuration
    new_config
        The new configuration for the connector

    Returns
    -------
    None

    Examples
    --------
    >>> from snorkelai.sdk.client import update_connector_config
    >>> new_config = {
    ...     "access_key_id": "new_access_key_id",
    ...     "secret_access_key": "new_secret_access_key",
    ...     "region": "new_region",
    ... }
    >>> update_connector_config(123, "new_name", new_config)
    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    config_obj = UpdateConfigRequestNewConfig.from_dict(new_config)
    request = UpdateConfigRequest(new_name=new_name, new_config=config_obj)

    update_connector_config_v1_connector_configs__config_uid__put(
        config_uid=config_uid, body=request, workspace_uid=workspace_uid
    )


def delete_connector_config(config_uid: int) -> None:
    """Delete a connector configuration.

    Parameters
    ----------
    config_uid
        The UID of the connector configuration to delete

    Returns
    -------
    None

    Examples
    --------
    >>> from snorkelai.sdk.client import delete_connector_config
    >>> delete_connector_config(123)
    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    delete_connector_config_v1_connector_configs__config_uid__delete(
        config_uid=config_uid, workspace_uid=workspace_uid
    )
