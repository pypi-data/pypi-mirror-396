from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.data_loader import DataLoader  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DataLoaderForIndexProvenance")


@attrs.define
class DataLoaderForIndexProvenance:
    """
    Attributes:
        data_loader_to_get_index_from (DataLoader): A class that is responsible for providing a 2d data to the caller

            The data should be immutable, i.e., it should be the same no matter when it is requested. E.g., a data loader
            for GT without versioning shouldn't exist.
        data_loaders (List['DataLoader']):
        transform_config_type (Union[Literal['index_provenance'], Unset]):  Default: 'index_provenance'.
    """

    data_loader_to_get_index_from: "DataLoader"
    data_loaders: List["DataLoader"]
    transform_config_type: Union[Literal["index_provenance"], Unset] = (
        "index_provenance"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_loader import DataLoader  # noqa: F401
        # fmt: on
        data_loader_to_get_index_from = self.data_loader_to_get_index_from.to_dict()
        data_loaders = []
        for data_loaders_item_data in self.data_loaders:
            data_loaders_item = data_loaders_item_data.to_dict()
            data_loaders.append(data_loaders_item)

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_loader_to_get_index_from": data_loader_to_get_index_from,
                "data_loaders": data_loaders,
            }
        )
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_loader import DataLoader  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        data_loader_to_get_index_from = DataLoader.from_dict(
            d.pop("data_loader_to_get_index_from")
        )

        data_loaders = []
        _data_loaders = d.pop("data_loaders")
        for data_loaders_item_data in _data_loaders:
            data_loaders_item = DataLoader.from_dict(data_loaders_item_data)

            data_loaders.append(data_loaders_item)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            data_loader_to_get_index_from=data_loader_to_get_index_from,
            data_loaders=data_loaders,
            transform_config_type=transform_config_type,
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
