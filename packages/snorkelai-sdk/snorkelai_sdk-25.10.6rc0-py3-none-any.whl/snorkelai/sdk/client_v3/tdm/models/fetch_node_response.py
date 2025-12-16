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
    from ..models.fetch_node_response_node_config import (
        FetchNodeResponseNodeConfig,  # noqa: F401
    )
    from ..models.label_schema import LabelSchema  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FetchNodeResponse")


@attrs.define
class FetchNodeResponse:
    """
    Attributes:
        node_cls (str):
        node_config (FetchNodeResponseNodeConfig):
        node_uid (int):
        application_uid (Union[Unset, int]):
        committed_op_version_uid (Union[Unset, int]):
        created_at (Union[Unset, datetime.datetime]):
        dataset_uid (Union[Unset, int]):
        expected_op_type (Union[Unset, str]):
        label_schema (Union[Unset, LabelSchema]):
    """

    node_cls: str
    node_config: "FetchNodeResponseNodeConfig"
    node_uid: int
    application_uid: Union[Unset, int] = UNSET
    committed_op_version_uid: Union[Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    dataset_uid: Union[Unset, int] = UNSET
    expected_op_type: Union[Unset, str] = UNSET
    label_schema: Union[Unset, "LabelSchema"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.fetch_node_response_node_config import (
            FetchNodeResponseNodeConfig,  # noqa: F401
        )
        from ..models.label_schema import LabelSchema  # noqa: F401
        # fmt: on
        node_cls = self.node_cls
        node_config = self.node_config.to_dict()
        node_uid = self.node_uid
        application_uid = self.application_uid
        committed_op_version_uid = self.committed_op_version_uid
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()
        dataset_uid = self.dataset_uid
        expected_op_type = self.expected_op_type
        label_schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_schema, Unset):
            label_schema = self.label_schema.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_cls": node_cls,
                "node_config": node_config,
                "node_uid": node_uid,
            }
        )
        if application_uid is not UNSET:
            field_dict["application_uid"] = application_uid
        if committed_op_version_uid is not UNSET:
            field_dict["committed_op_version_uid"] = committed_op_version_uid
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if expected_op_type is not UNSET:
            field_dict["expected_op_type"] = expected_op_type
        if label_schema is not UNSET:
            field_dict["label_schema"] = label_schema

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.fetch_node_response_node_config import (
            FetchNodeResponseNodeConfig,  # noqa: F401
        )
        from ..models.label_schema import LabelSchema  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        node_cls = d.pop("node_cls")

        node_config = FetchNodeResponseNodeConfig.from_dict(d.pop("node_config"))

        node_uid = d.pop("node_uid")

        _application_uid = d.pop("application_uid", UNSET)
        application_uid = UNSET if _application_uid is None else _application_uid

        _committed_op_version_uid = d.pop("committed_op_version_uid", UNSET)
        committed_op_version_uid = (
            UNSET if _committed_op_version_uid is None else _committed_op_version_uid
        )

        _created_at = d.pop("created_at", UNSET)
        _created_at = UNSET if _created_at is None else _created_at
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _expected_op_type = d.pop("expected_op_type", UNSET)
        expected_op_type = UNSET if _expected_op_type is None else _expected_op_type

        _label_schema = d.pop("label_schema", UNSET)
        _label_schema = UNSET if _label_schema is None else _label_schema
        label_schema: Union[Unset, LabelSchema]
        if isinstance(_label_schema, Unset):
            label_schema = UNSET
        else:
            label_schema = LabelSchema.from_dict(_label_schema)

        obj = cls(
            node_cls=node_cls,
            node_config=node_config,
            node_uid=node_uid,
            application_uid=application_uid,
            committed_op_version_uid=committed_op_version_uid,
            created_at=created_at,
            dataset_uid=dataset_uid,
            expected_op_type=expected_op_type,
            label_schema=label_schema,
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
