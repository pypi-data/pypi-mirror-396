import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
    from ..models.list_datasets_response_hydrated_node_dag import (
        ListDatasetsResponseHydratedNodeDag,  # noqa: F401
    )
    from ..models.list_datasets_response_node_dag import (
        ListDatasetsResponseNodeDag,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ListDatasetsResponse")


@attrs.define
class ListDatasetsResponse:
    """
    Attributes:
        are_all_datasources_arrow (bool):
        dataset_uid (int):
        name (str):
        node_dag (ListDatasetsResponseNodeDag):
        file_storage_config_uid (Union[Unset, int]):
        first_created (Union[Unset, datetime.date]):
        hydrated_node_dag (Union[Unset, ListDatasetsResponseHydratedNodeDag]):
        last_opened (Union[Unset, datetime.datetime]):
        metadata (Union[Unset, DatasetMetadata]):
        total_size_bytes (Union[Unset, int]):
        workspace_uid (Union[Unset, int]):  Default: 1.
    """

    are_all_datasources_arrow: bool
    dataset_uid: int
    name: str
    node_dag: "ListDatasetsResponseNodeDag"
    file_storage_config_uid: Union[Unset, int] = UNSET
    first_created: Union[Unset, datetime.date] = UNSET
    hydrated_node_dag: Union[Unset, "ListDatasetsResponseHydratedNodeDag"] = UNSET
    last_opened: Union[Unset, datetime.datetime] = UNSET
    metadata: Union[Unset, "DatasetMetadata"] = UNSET
    total_size_bytes: Union[Unset, int] = UNSET
    workspace_uid: Union[Unset, int] = 1
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
        from ..models.list_datasets_response_hydrated_node_dag import (
            ListDatasetsResponseHydratedNodeDag,  # noqa: F401
        )
        from ..models.list_datasets_response_node_dag import (
            ListDatasetsResponseNodeDag,  # noqa: F401
        )
        # fmt: on
        are_all_datasources_arrow = self.are_all_datasources_arrow
        dataset_uid = self.dataset_uid
        name = self.name
        node_dag = self.node_dag.to_dict()
        file_storage_config_uid = self.file_storage_config_uid
        first_created: Union[Unset, str] = UNSET
        if not isinstance(self.first_created, Unset):
            first_created = self.first_created.isoformat()
        hydrated_node_dag: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.hydrated_node_dag, Unset):
            hydrated_node_dag = self.hydrated_node_dag.to_dict()
        last_opened: Union[Unset, str] = UNSET
        if not isinstance(self.last_opened, Unset):
            last_opened = self.last_opened.isoformat()
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        total_size_bytes = self.total_size_bytes
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "are_all_datasources_arrow": are_all_datasources_arrow,
                "dataset_uid": dataset_uid,
                "name": name,
                "node_dag": node_dag,
            }
        )
        if file_storage_config_uid is not UNSET:
            field_dict["file_storage_config_uid"] = file_storage_config_uid
        if first_created is not UNSET:
            field_dict["first_created"] = first_created
        if hydrated_node_dag is not UNSET:
            field_dict["hydrated_node_dag"] = hydrated_node_dag
        if last_opened is not UNSET:
            field_dict["last_opened"] = last_opened
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if total_size_bytes is not UNSET:
            field_dict["total_size_bytes"] = total_size_bytes
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
        from ..models.list_datasets_response_hydrated_node_dag import (
            ListDatasetsResponseHydratedNodeDag,  # noqa: F401
        )
        from ..models.list_datasets_response_node_dag import (
            ListDatasetsResponseNodeDag,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        are_all_datasources_arrow = d.pop("are_all_datasources_arrow")

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        node_dag = ListDatasetsResponseNodeDag.from_dict(d.pop("node_dag"))

        _file_storage_config_uid = d.pop("file_storage_config_uid", UNSET)
        file_storage_config_uid = (
            UNSET if _file_storage_config_uid is None else _file_storage_config_uid
        )

        _first_created = d.pop("first_created", UNSET)
        _first_created = UNSET if _first_created is None else _first_created
        first_created: Union[Unset, datetime.date]
        if isinstance(_first_created, Unset):
            first_created = UNSET
        else:
            first_created = isoparse(_first_created).date()

        _hydrated_node_dag = d.pop("hydrated_node_dag", UNSET)
        _hydrated_node_dag = UNSET if _hydrated_node_dag is None else _hydrated_node_dag
        hydrated_node_dag: Union[Unset, ListDatasetsResponseHydratedNodeDag]
        if isinstance(_hydrated_node_dag, Unset):
            hydrated_node_dag = UNSET
        else:
            hydrated_node_dag = ListDatasetsResponseHydratedNodeDag.from_dict(
                _hydrated_node_dag
            )

        _last_opened = d.pop("last_opened", UNSET)
        _last_opened = UNSET if _last_opened is None else _last_opened
        last_opened: Union[Unset, datetime.datetime]
        if isinstance(_last_opened, Unset):
            last_opened = UNSET
        else:
            last_opened = isoparse(_last_opened)

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, DatasetMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DatasetMetadata.from_dict(_metadata)

        _total_size_bytes = d.pop("total_size_bytes", UNSET)
        total_size_bytes = UNSET if _total_size_bytes is None else _total_size_bytes

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            are_all_datasources_arrow=are_all_datasources_arrow,
            dataset_uid=dataset_uid,
            name=name,
            node_dag=node_dag,
            file_storage_config_uid=file_storage_config_uid,
            first_created=first_created,
            hydrated_node_dag=hydrated_node_dag,
            last_opened=last_opened,
            metadata=metadata,
            total_size_bytes=total_size_bytes,
            workspace_uid=workspace_uid,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
