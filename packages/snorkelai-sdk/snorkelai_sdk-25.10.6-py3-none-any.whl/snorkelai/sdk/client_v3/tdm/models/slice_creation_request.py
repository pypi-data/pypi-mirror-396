from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.slice_creation_request_metadata import (
        SliceCreationRequestMetadata,  # noqa: F401
    )
    from ..models.slice_template_graph import SliceTemplateGraph  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SliceCreationRequest")


@attrs.define
class SliceCreationRequest:
    """
    Attributes:
        dataset_uid (int):
        display_name (str):
        description (Union[Unset, str]):
        filter_config_str (Union[Unset, str]):
        metadata (Union[Unset, SliceCreationRequestMetadata]):
        template_graph (Union[Unset, SliceTemplateGraph]):
        user_uid (Union[Unset, int]):
        x_uids (Union[Unset, List[str]]):
    """

    dataset_uid: int
    display_name: str
    description: Union[Unset, str] = UNSET
    filter_config_str: Union[Unset, str] = UNSET
    metadata: Union[Unset, "SliceCreationRequestMetadata"] = UNSET
    template_graph: Union[Unset, "SliceTemplateGraph"] = UNSET
    user_uid: Union[Unset, int] = UNSET
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.slice_creation_request_metadata import (
            SliceCreationRequestMetadata,  # noqa: F401
        )
        from ..models.slice_template_graph import SliceTemplateGraph  # noqa: F401
        # fmt: on
        dataset_uid = self.dataset_uid
        display_name = self.display_name
        description = self.description
        filter_config_str = self.filter_config_str
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        template_graph: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.template_graph, Unset):
            template_graph = self.template_graph.to_dict()
        user_uid = self.user_uid
        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
                "display_name": display_name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if filter_config_str is not UNSET:
            field_dict["filter_config_str"] = filter_config_str
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if template_graph is not UNSET:
            field_dict["template_graph"] = template_graph
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.slice_creation_request_metadata import (
            SliceCreationRequestMetadata,  # noqa: F401
        )
        from ..models.slice_template_graph import SliceTemplateGraph  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        display_name = d.pop("display_name")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _filter_config_str = d.pop("filter_config_str", UNSET)
        filter_config_str = UNSET if _filter_config_str is None else _filter_config_str

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, SliceCreationRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SliceCreationRequestMetadata.from_dict(_metadata)

        _template_graph = d.pop("template_graph", UNSET)
        _template_graph = UNSET if _template_graph is None else _template_graph
        template_graph: Union[Unset, SliceTemplateGraph]
        if isinstance(_template_graph, Unset):
            template_graph = UNSET
        else:
            template_graph = SliceTemplateGraph.from_dict(_template_graph)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            dataset_uid=dataset_uid,
            display_name=display_name,
            description=description,
            filter_config_str=filter_config_str,
            metadata=metadata,
            template_graph=template_graph,
            user_uid=user_uid,
            x_uids=x_uids,
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
