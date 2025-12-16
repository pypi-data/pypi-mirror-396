from typing import Dict, List, Optional

from snorkelai.sdk.client_v3.tdm.api.sources import (
    add_source_sources_post,
    delete_source_sources__source_uid__delete,
    get_sources_sources_get,
    update_source_sources__source_uid__put,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AddSourceParams,
    AddSourceParamsMetadata,
    UpdateSourceParams,
    UpdateSourceParamsMetadata,
)
from snorkelai.sdk.client_v3.users import get_user
from snorkelai.sdk.client_v3.utils import (
    _create_params_instance_or_unset_from_metadata,
    _wrap_in_unset,
    get_source_uid,
    get_workspace_uid,
)
from snorkelai.sdk.context.ctx import SnorkelSDKContext


class Source:
    def __init__(
        self,
        source_uid: int,
        source_type: str,
        source_name: str,
        user_uid: Optional[int] = None,
        metadata: Optional[dict] = None,
    ):
        self.source_uid = source_uid
        self.source_type = source_type
        self.source_name = source_name
        self.user_uid = user_uid
        self.metadata = metadata

    @classmethod
    def from_dict(cls, source: dict) -> "Source":
        return cls(
            source_uid=source["source_uid"],
            source_type=source["source_type"],
            source_name=source["source_name"],
            user_uid=source.get("user_uid"),
            metadata=source.get("metadata"),
        )

    def to_dict(self) -> Dict:
        return {
            "source_uid": self.source_uid,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "user_uid": self.user_uid,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return str(self.to_dict())


def create_annotation_source(
    username: Optional[str] = None,
    source_name: Optional[str] = None,
    source_type: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Source:
    """Create an annotation source.

    Parameters
    ----------
    username
        The username of source if the source type is user.
    source_name
        The name of the source, which defaults to username for user type of source.
    source_type
        The type of source (user, aggregation, etc)
    metadata
        Any source metadata

    Returns
    -------
    Source
        The created source.

    """
    user_uid = get_user(username)["user_uid"] if username else None
    source_params_metadata = _create_params_instance_or_unset_from_metadata(
        AddSourceParamsMetadata, metadata
    )
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)

    source_params = AddSourceParams(
        metadata=source_params_metadata,
        source_name=_wrap_in_unset(source_name),
        source_type=_wrap_in_unset(source_type),
        user_uid=_wrap_in_unset(user_uid),
        workspace_uid=workspace_uid,
    )
    response = add_source_sources_post(body=source_params)
    return Source.from_dict(response.created_source.to_dict())


def get_annotation_source(
    source_name: Optional[str] = None, source_uid: Optional[int] = None
) -> Source:
    """Get an annotation source from uid or name.

    Parameters
    ----------
    source_name
        Name of the source (such as username, etc).
    source_uid
        Uid of the source.

    Returns
    -------
    A single source that matches name and/or uid

    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)
    if not (source_uid or source_name):
        raise ValueError("Either source_uid or source_name must be present")
    if source_uid and source_name:
        raise ValueError("Only one of source_uid or source_name should be present")
    response = get_sources_sources_get(workspace_uid=workspace_uid)
    for source in response.sources:
        if source_name and source.source_name != source_name:
            continue
        if source_uid and source.source_uid != source_uid:
            continue
        return Source.from_dict(source.to_dict())

    raise ValueError(
        f"Source with source_uid {source_uid} and source name {source_name} does not exist"
    )


def get_annotation_sources() -> List[Source]:
    """Get annotation sources.

    Returns
    -------
    List[Source]
        A list of sources.

    """
    workspace_name = SnorkelSDKContext.get_global().workspace_name
    workspace_uid = get_workspace_uid(workspace_name)
    response = get_sources_sources_get(workspace_uid=workspace_uid)
    return [Source.from_dict(source.to_dict()) for source in response.sources]


def update_annotation_source(
    source_name: str,
    new_source_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Source:
    """Update an annotation source.

    Parameters
    ----------
    source_name
        The current name of the source.
    new_source_name
        The new name of the source.
    metadata
        The updated metadata.

    Returns
    -------
    Source
        The updated source.

    """
    source_uid = get_source_uid(source_name)
    source_params_metadata = _create_params_instance_or_unset_from_metadata(
        UpdateSourceParamsMetadata, metadata
    )
    source_params = UpdateSourceParams(
        metadata=source_params_metadata, source_name=_wrap_in_unset(new_source_name)
    )
    response = update_source_sources__source_uid__put(source_uid, body=source_params)
    return Source.from_dict(response.to_dict())


def delete_annotation_source(source_name: str) -> bool:
    """Delete an annotation source.

    Parameters
    ----------
    source_name
        The name of the source.

    Returns
    -------
    bool
        Returns true if the operation succeeds.

    """
    source_uid = get_source_uid(source_name)
    delete_source_sources__source_uid__delete(source_uid)
    return True
