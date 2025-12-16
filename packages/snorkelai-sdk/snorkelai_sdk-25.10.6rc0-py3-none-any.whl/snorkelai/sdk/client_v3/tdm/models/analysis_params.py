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

from ..models.datasource_type import DatasourceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.source_spec import SourceSpec  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnalysisParams")


@attrs.define
class AnalysisParams:
    """Parameters for analyzing a data source.

    Attributes:
        source_type (DatasourceType): Types of data sources that can be connected to.
        sources (List['SourceSpec']):
        data_connector_config_uid (Union[Unset, int]):
        uid_col (Union[Unset, str]):
    """

    source_type: DatasourceType
    sources: List["SourceSpec"]
    data_connector_config_uid: Union[Unset, int] = UNSET
    uid_col: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.source_spec import SourceSpec  # noqa: F401
        # fmt: on
        source_type = self.source_type.value
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        data_connector_config_uid = self.data_connector_config_uid
        uid_col = self.uid_col

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_type": source_type,
                "sources": sources,
            }
        )
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if uid_col is not UNSET:
            field_dict["uid_col"] = uid_col

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.source_spec import SourceSpec  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        source_type = DatasourceType(d.pop("source_type"))

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = SourceSpec.from_dict(sources_item_data)

            sources.append(sources_item)

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _uid_col = d.pop("uid_col", UNSET)
        uid_col = UNSET if _uid_col is None else _uid_col

        obj = cls(
            source_type=source_type,
            sources=sources,
            data_connector_config_uid=data_connector_config_uid,
            uid_col=uid_col,
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
