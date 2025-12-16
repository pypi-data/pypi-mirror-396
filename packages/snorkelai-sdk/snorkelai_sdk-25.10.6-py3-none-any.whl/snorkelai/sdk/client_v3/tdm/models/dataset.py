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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
    from ..models.dataset_node_dag import DatasetNodeDag  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Dataset")


@attrs.define
class Dataset:
    """
    Attributes:
        dataset_uid (int):
        name (str):
        workspace_uid (int):
        metadata (Union[Unset, DatasetMetadata]):
        node_dag (Union[Unset, DatasetNodeDag]):
    """

    dataset_uid: int
    name: str
    workspace_uid: int
    metadata: Union[Unset, "DatasetMetadata"] = UNSET
    node_dag: Union[Unset, "DatasetNodeDag"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
        from ..models.dataset_node_dag import DatasetNodeDag  # noqa: F401
        # fmt: on
        dataset_uid = self.dataset_uid
        name = self.name
        workspace_uid = self.workspace_uid
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        node_dag: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.node_dag, Unset):
            node_dag = self.node_dag.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "name": name,
                "workspace_uid": workspace_uid,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if node_dag is not UNSET:
            field_dict["node_dag"] = node_dag

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.dataset_metadata import DatasetMetadata  # noqa: F401
        from ..models.dataset_node_dag import DatasetNodeDag  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        workspace_uid = d.pop("workspace_uid")

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, DatasetMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DatasetMetadata.from_dict(_metadata)

        _node_dag = d.pop("node_dag", UNSET)
        _node_dag = UNSET if _node_dag is None else _node_dag
        node_dag: Union[Unset, DatasetNodeDag]
        if isinstance(_node_dag, Unset):
            node_dag = UNSET
        else:
            node_dag = DatasetNodeDag.from_dict(_node_dag)

        obj = cls(
            dataset_uid=dataset_uid,
            name=name,
            workspace_uid=workspace_uid,
            metadata=metadata,
            node_dag=node_dag,
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
