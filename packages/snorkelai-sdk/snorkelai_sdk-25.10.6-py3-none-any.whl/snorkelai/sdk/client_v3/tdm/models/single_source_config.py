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
    from ..models.single_source_config_credential_kwargs import (
        SingleSourceConfigCredentialKwargs,  # noqa: F401
    )
    from ..models.single_source_config_reader_kwargs import (
        SingleSourceConfigReaderKwargs,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SingleSourceConfig")


@attrs.define
class SingleSourceConfig:
    """
    Attributes:
        source (str): Path, query, or other identifier for the data source
        source_type (DatasourceType): Types of data sources that can be connected to.
        credential_kwargs (Union[Unset, SingleSourceConfigCredentialKwargs]):
        data_connector_config_uid (Union[Unset, int]):
        reader_kwargs (Union[Unset, SingleSourceConfigReaderKwargs]):
    """

    source: str
    source_type: DatasourceType
    credential_kwargs: Union[Unset, "SingleSourceConfigCredentialKwargs"] = UNSET
    data_connector_config_uid: Union[Unset, int] = UNSET
    reader_kwargs: Union[Unset, "SingleSourceConfigReaderKwargs"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.single_source_config_credential_kwargs import (
            SingleSourceConfigCredentialKwargs,  # noqa: F401
        )
        from ..models.single_source_config_reader_kwargs import (
            SingleSourceConfigReaderKwargs,  # noqa: F401
        )
        # fmt: on
        source = self.source
        source_type = self.source_type.value
        credential_kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.credential_kwargs, Unset):
            credential_kwargs = self.credential_kwargs.to_dict()
        data_connector_config_uid = self.data_connector_config_uid
        reader_kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reader_kwargs, Unset):
            reader_kwargs = self.reader_kwargs.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "source_type": source_type,
            }
        )
        if credential_kwargs is not UNSET:
            field_dict["credential_kwargs"] = credential_kwargs
        if data_connector_config_uid is not UNSET:
            field_dict["data_connector_config_uid"] = data_connector_config_uid
        if reader_kwargs is not UNSET:
            field_dict["reader_kwargs"] = reader_kwargs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.single_source_config_credential_kwargs import (
            SingleSourceConfigCredentialKwargs,  # noqa: F401
        )
        from ..models.single_source_config_reader_kwargs import (
            SingleSourceConfigReaderKwargs,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        source = d.pop("source")

        source_type = DatasourceType(d.pop("source_type"))

        _credential_kwargs = d.pop("credential_kwargs", UNSET)
        _credential_kwargs = UNSET if _credential_kwargs is None else _credential_kwargs
        credential_kwargs: Union[Unset, SingleSourceConfigCredentialKwargs]
        if isinstance(_credential_kwargs, Unset):
            credential_kwargs = UNSET
        else:
            credential_kwargs = SingleSourceConfigCredentialKwargs.from_dict(
                _credential_kwargs
            )

        _data_connector_config_uid = d.pop("data_connector_config_uid", UNSET)
        data_connector_config_uid = (
            UNSET if _data_connector_config_uid is None else _data_connector_config_uid
        )

        _reader_kwargs = d.pop("reader_kwargs", UNSET)
        _reader_kwargs = UNSET if _reader_kwargs is None else _reader_kwargs
        reader_kwargs: Union[Unset, SingleSourceConfigReaderKwargs]
        if isinstance(_reader_kwargs, Unset):
            reader_kwargs = UNSET
        else:
            reader_kwargs = SingleSourceConfigReaderKwargs.from_dict(_reader_kwargs)

        obj = cls(
            source=source,
            source_type=source_type,
            credential_kwargs=credential_kwargs,
            data_connector_config_uid=data_connector_config_uid,
            reader_kwargs=reader_kwargs,
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
