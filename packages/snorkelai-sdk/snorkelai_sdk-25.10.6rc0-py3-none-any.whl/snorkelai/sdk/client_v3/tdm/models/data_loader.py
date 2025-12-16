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
    from ..models.data_loader_config import DataLoaderConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="DataLoader")


@attrs.define
class DataLoader:
    """A class that is responsible for providing a 2d data to the caller

    The data should be immutable, i.e., it should be the same no matter when it is requested. E.g., a data loader for GT
    without versioning shouldn't exist.

        Attributes:
            config (DataLoaderConfig):
            type (str):
            calc_signature_at_init (Union[Unset, bool]):  Default: False.
            index_signature_at_init (Union[Unset, str]):
            value_signature_at_init (Union[Unset, str]):
    """

    config: "DataLoaderConfig"
    type: str
    calc_signature_at_init: Union[Unset, bool] = False
    index_signature_at_init: Union[Unset, str] = UNSET
    value_signature_at_init: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_loader_config import DataLoaderConfig  # noqa: F401
        # fmt: on
        config = self.config.to_dict()
        type = self.type
        calc_signature_at_init = self.calc_signature_at_init
        index_signature_at_init = self.index_signature_at_init
        value_signature_at_init = self.value_signature_at_init

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "type": type,
            }
        )
        if calc_signature_at_init is not UNSET:
            field_dict["calc_signature_at_init"] = calc_signature_at_init
        if index_signature_at_init is not UNSET:
            field_dict["index_signature_at_init"] = index_signature_at_init
        if value_signature_at_init is not UNSET:
            field_dict["value_signature_at_init"] = value_signature_at_init

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_loader_config import DataLoaderConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        config = DataLoaderConfig.from_dict(d.pop("config"))

        type = d.pop("type")

        _calc_signature_at_init = d.pop("calc_signature_at_init", UNSET)
        calc_signature_at_init = (
            UNSET if _calc_signature_at_init is None else _calc_signature_at_init
        )

        _index_signature_at_init = d.pop("index_signature_at_init", UNSET)
        index_signature_at_init = (
            UNSET if _index_signature_at_init is None else _index_signature_at_init
        )

        _value_signature_at_init = d.pop("value_signature_at_init", UNSET)
        value_signature_at_init = (
            UNSET if _value_signature_at_init is None else _value_signature_at_init
        )

        obj = cls(
            config=config,
            type=type,
            calc_signature_at_init=calc_signature_at_init,
            index_signature_at_init=index_signature_at_init,
            value_signature_at_init=value_signature_at_init,
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
