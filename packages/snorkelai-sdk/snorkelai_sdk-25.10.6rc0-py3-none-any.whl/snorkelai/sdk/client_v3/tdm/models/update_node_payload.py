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
    from ..models.committed_operator_config import CommittedOperatorConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="UpdateNodePayload")


@attrs.define
class UpdateNodePayload:
    """One must either include
    - A referenced Operator UID, in which case we grab that op_type/op_config and make
      a new OpVersion, then commit that OpVersion to the Node
    - A referenced OpVersion UID, in which case we simply commit that version to the Node
    - A group of op_type/op_config values, in which case we make a new OpVersion and commit it
      to the Node
    - If none of those are supplied (i.e. all keys are missing or they all map to None), we assume the user is
      trying to uncommit any version from the Node entirely (i.e. set op_type/op_config to None)

        Attributes:
            config (Union[Unset, CommittedOperatorConfig]):
            op_version_uid (Union[Unset, int]):
            operator_uid (Union[Unset, int]):
    """

    config: Union[Unset, "CommittedOperatorConfig"] = UNSET
    op_version_uid: Union[Unset, int] = UNSET
    operator_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.committed_operator_config import (
            CommittedOperatorConfig,  # noqa: F401
        )
        # fmt: on
        config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()
        op_version_uid = self.op_version_uid
        operator_uid = self.operator_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if op_version_uid is not UNSET:
            field_dict["op_version_uid"] = op_version_uid
        if operator_uid is not UNSET:
            field_dict["operator_uid"] = operator_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.committed_operator_config import (
            CommittedOperatorConfig,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _config = d.pop("config", UNSET)
        _config = UNSET if _config is None else _config
        config: Union[Unset, CommittedOperatorConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = CommittedOperatorConfig.from_dict(_config)

        _op_version_uid = d.pop("op_version_uid", UNSET)
        op_version_uid = UNSET if _op_version_uid is None else _op_version_uid

        _operator_uid = d.pop("operator_uid", UNSET)
        operator_uid = UNSET if _operator_uid is None else _operator_uid

        obj = cls(
            config=config,
            op_version_uid=op_version_uid,
            operator_uid=operator_uid,
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
