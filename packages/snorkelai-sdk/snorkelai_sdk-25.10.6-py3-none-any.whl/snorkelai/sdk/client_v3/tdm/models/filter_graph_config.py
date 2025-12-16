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
    from ..models.filter_condition import FilterCondition  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="FilterGraphConfig")


@attrs.define
class FilterGraphConfig:
    """
    Attributes:
        graph (FilterCondition): A filter condition maps a data point to a boolean of whether the condition applies

            This is the primary logic for a filter.
            Note that a Filter condition may be composed of one or more conditions being combined.
        transform_config_type (Union[Literal['filter_graph'], Unset]):  Default: 'filter_graph'.
    """

    graph: "FilterCondition"
    transform_config_type: Union[Literal["filter_graph"], Unset] = "filter_graph"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.filter_condition import FilterCondition  # noqa: F401
        # fmt: on
        graph = self.graph.to_dict()
        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "graph": graph,
            }
        )
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.filter_condition import FilterCondition  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        graph = FilterCondition.from_dict(d.pop("graph"))

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            graph=graph,
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
