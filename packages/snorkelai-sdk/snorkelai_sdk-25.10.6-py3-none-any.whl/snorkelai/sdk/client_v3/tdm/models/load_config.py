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

from ..models.source_type import SourceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.load_config_col_types import LoadConfigColTypes  # noqa: F401
    from ..models.load_config_reader_kwargs import LoadConfigReaderKwargs  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LoadConfig")


@attrs.define
class LoadConfig:
    """
    Attributes:
        path (str):
        col_types (Union[Unset, LoadConfigColTypes]):
        context_datasource_uid (Union[Unset, int]):
        credential_kwargs (Union[Unset, str]):
        data_connector_config_uid (Union[Unset, int]):
        ds_schema_version (Union[Unset, int]):  Default: 0.
        parent_datasource_uid (Union[Unset, int]):
        reader_kwargs (Union[Unset, LoadConfigReaderKwargs]):
        references (Union[Unset, List[int]]):
        type (Union[Unset, SourceType]):
        uid_col (Union[Unset, str]):
    """

    path: str
    col_types: Union[Unset, "LoadConfigColTypes"] = UNSET
    context_datasource_uid: Union[Unset, int] = UNSET
    credential_kwargs: Union[Unset, str] = UNSET
    data_connector_config_uid: Union[Unset, int] = UNSET
    ds_schema_version: Union[Unset, int] = 0
    parent_datasource_uid: Union[Unset, int] = UNSET
    reader_kwargs: Union[Unset, "LoadConfigReaderKwargs"] = UNSET
    references: Union[Unset, List[int]] = UNSET
    type: Union[Unset, SourceType] = UNSET
    uid_col: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.load_config_col_types import LoadConfigColTypes  # noqa: F401
        from ..models.load_config_reader_kwargs import (
            LoadConfigReaderKwargs,  # noqa: F401
        )
        # fmt: on
        path = self.path
        col_types: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.col_types, Unset):
            col_types = self.col_types.to_dict()
        context_datasource_uid = self.context_datasource_uid
        credential_kwargs = self.credential_kwargs
        data_connector_config_uid = self.data_connector_config_uid
        ds_schema_version = self.ds_schema_version
        parent_datasource_uid = self.parent_datasource_uid
        reader_kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reader_kwargs, Unset):
            reader_kwargs = self.reader_kwargs.to_dict()
        references: Union[Unset, List[int]] = UNSET
        if not isinstance(self.references, Unset):
            references = self.references

        type: Union[Unset, int] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        uid_col = self.uid_col

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
            }
        )
        if col_types is not UNSET:
            field_dict["col_types"] = col_types
        if context_datasource_uid is not UNSET:
            field_dict["context_datasource_uid"] = context_datasource_uid
        if credential_kwargs is not UNSET:
            field_dict["credential_kwargs"] = credential_kwargs
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if ds_schema_version is not UNSET:
            field_dict["ds_schema_version"] = ds_schema_version
        if parent_datasource_uid is not UNSET:
            field_dict["parent_datasource_uid"] = parent_datasource_uid
        if reader_kwargs is not UNSET:
            field_dict["reader_kwargs"] = reader_kwargs
        if references is not UNSET:
            field_dict["references"] = references
        if type is not UNSET:
            field_dict["type"] = type
        if uid_col is not UNSET:
            field_dict["uid_col"] = uid_col

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.load_config_col_types import LoadConfigColTypes  # noqa: F401
        from ..models.load_config_reader_kwargs import (
            LoadConfigReaderKwargs,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        path = d.pop("path")

        _col_types = d.pop("col_types", UNSET)
        _col_types = UNSET if _col_types is None else _col_types
        col_types: Union[Unset, LoadConfigColTypes]
        if isinstance(_col_types, Unset):
            col_types = UNSET
        else:
            col_types = LoadConfigColTypes.from_dict(_col_types)

        _context_datasource_uid = d.pop("context_datasource_uid", UNSET)
        context_datasource_uid = (
            UNSET if _context_datasource_uid is None else _context_datasource_uid
        )

        _credential_kwargs = d.pop("credential_kwargs", UNSET)
        credential_kwargs = UNSET if _credential_kwargs is None else _credential_kwargs

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _ds_schema_version = d.pop("ds_schema_version", UNSET)
        ds_schema_version = UNSET if _ds_schema_version is None else _ds_schema_version

        _parent_datasource_uid = d.pop("parent_datasource_uid", UNSET)
        parent_datasource_uid = (
            UNSET if _parent_datasource_uid is None else _parent_datasource_uid
        )

        _reader_kwargs = d.pop("reader_kwargs", UNSET)
        _reader_kwargs = UNSET if _reader_kwargs is None else _reader_kwargs
        reader_kwargs: Union[Unset, LoadConfigReaderKwargs]
        if isinstance(_reader_kwargs, Unset):
            reader_kwargs = UNSET
        else:
            reader_kwargs = LoadConfigReaderKwargs.from_dict(_reader_kwargs)

        _references = d.pop("references", UNSET)
        references = cast(List[int], UNSET if _references is None else _references)

        _type = d.pop("type", UNSET)
        _type = UNSET if _type is None else _type
        type: Union[Unset, SourceType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = SourceType(_type)

        _uid_col = d.pop("uid_col", UNSET)
        uid_col = UNSET if _uid_col is None else _uid_col

        obj = cls(
            path=path,
            col_types=col_types,
            context_datasource_uid=context_datasource_uid,
            credential_kwargs=credential_kwargs,
            data_connector_config_uid=data_connector_config_uid,
            ds_schema_version=ds_schema_version,
            parent_datasource_uid=parent_datasource_uid,
            reader_kwargs=reader_kwargs,
            references=references,
            type=type,
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
