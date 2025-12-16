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
    from ..models.committed_operator_payload import (
        CommittedOperatorPayload,  # noqa: F401
    )
    from ..models.create_node_payload_node_config import (
        CreateNodePayloadNodeConfig,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateNodePayload")


@attrs.define
class CreateNodePayload:
    """
    Attributes:
        input_node_uids (List[int]):
        add_to_parent_block (Union[Unset, bool]):  Default: False.
        committed_operator_config (Union[Unset, CommittedOperatorPayload]):
        expected_op_type (Union[Unset, str]):
        label_schema_uid (Union[Unset, int]):
        node_cls (Union[Unset, str]):  Default: 'ApplicationNode'.
        node_config (Union[Unset, CreateNodePayloadNodeConfig]):
        output_node_uids (Union[Unset, List[int]]):
        skip_validation (Union[Unset, bool]):  Default: False.
    """

    input_node_uids: List[int]
    add_to_parent_block: Union[Unset, bool] = False
    committed_operator_config: Union[Unset, "CommittedOperatorPayload"] = UNSET
    expected_op_type: Union[Unset, str] = UNSET
    label_schema_uid: Union[Unset, int] = UNSET
    node_cls: Union[Unset, str] = "ApplicationNode"
    node_config: Union[Unset, "CreateNodePayloadNodeConfig"] = UNSET
    output_node_uids: Union[Unset, List[int]] = UNSET
    skip_validation: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.committed_operator_payload import (
            CommittedOperatorPayload,  # noqa: F401
        )
        from ..models.create_node_payload_node_config import (
            CreateNodePayloadNodeConfig,  # noqa: F401
        )
        # fmt: on
        input_node_uids = self.input_node_uids

        add_to_parent_block = self.add_to_parent_block
        committed_operator_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.committed_operator_config, Unset):
            committed_operator_config = self.committed_operator_config.to_dict()
        expected_op_type = self.expected_op_type
        label_schema_uid = self.label_schema_uid
        node_cls = self.node_cls
        node_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.node_config, Unset):
            node_config = self.node_config.to_dict()
        output_node_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.output_node_uids, Unset):
            output_node_uids = self.output_node_uids

        skip_validation = self.skip_validation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_node_uids": input_node_uids,
            }
        )
        if add_to_parent_block is not UNSET:
            field_dict["add_to_parent_block"] = add_to_parent_block
        if committed_operator_config is not UNSET:
            field_dict["committed_operator_config"] = committed_operator_config
        if expected_op_type is not UNSET:
            field_dict["expected_op_type"] = expected_op_type
        if label_schema_uid is not UNSET:
            field_dict["label_schema_uid"] = label_schema_uid
        if node_cls is not UNSET:
            field_dict["node_cls"] = node_cls
        if node_config is not UNSET:
            field_dict["node_config"] = node_config
        if output_node_uids is not UNSET:
            field_dict["output_node_uids"] = output_node_uids
        if skip_validation is not UNSET:
            field_dict["skip_validation"] = skip_validation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.committed_operator_payload import (
            CommittedOperatorPayload,  # noqa: F401
        )
        from ..models.create_node_payload_node_config import (
            CreateNodePayloadNodeConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        input_node_uids = cast(List[int], d.pop("input_node_uids"))

        _add_to_parent_block = d.pop("add_to_parent_block", UNSET)
        add_to_parent_block = (
            UNSET if _add_to_parent_block is None else _add_to_parent_block
        )

        _committed_operator_config = d.pop("committed_operator_config", UNSET)
        _committed_operator_config = (
            UNSET if _committed_operator_config is None else _committed_operator_config
        )
        committed_operator_config: Union[Unset, CommittedOperatorPayload]
        if isinstance(_committed_operator_config, Unset):
            committed_operator_config = UNSET
        else:
            committed_operator_config = CommittedOperatorPayload.from_dict(
                _committed_operator_config
            )

        _expected_op_type = d.pop("expected_op_type", UNSET)
        expected_op_type = UNSET if _expected_op_type is None else _expected_op_type

        _label_schema_uid = d.pop("label_schema_uid", UNSET)
        label_schema_uid = UNSET if _label_schema_uid is None else _label_schema_uid

        _node_cls = d.pop("node_cls", UNSET)
        node_cls = UNSET if _node_cls is None else _node_cls

        _node_config = d.pop("node_config", UNSET)
        _node_config = UNSET if _node_config is None else _node_config
        node_config: Union[Unset, CreateNodePayloadNodeConfig]
        if isinstance(_node_config, Unset):
            node_config = UNSET
        else:
            node_config = CreateNodePayloadNodeConfig.from_dict(_node_config)

        _output_node_uids = d.pop("output_node_uids", UNSET)
        output_node_uids = cast(
            List[int], UNSET if _output_node_uids is None else _output_node_uids
        )

        _skip_validation = d.pop("skip_validation", UNSET)
        skip_validation = UNSET if _skip_validation is None else _skip_validation

        obj = cls(
            input_node_uids=input_node_uids,
            add_to_parent_block=add_to_parent_block,
            committed_operator_config=committed_operator_config,
            expected_op_type=expected_op_type,
            label_schema_uid=label_schema_uid,
            node_cls=node_cls,
            node_config=node_config,
            output_node_uids=output_node_uids,
            skip_validation=skip_validation,
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
