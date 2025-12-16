from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.benchmark_populator_metadata import (
        BenchmarkPopulatorMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ListBenchmarkPopulatorsResponse")


@attrs.define
class ListBenchmarkPopulatorsResponse:
    """Response model for listing benchmark populators.

    Attributes:
        populators (List['BenchmarkPopulatorMetadata']):
    """

    populators: List["BenchmarkPopulatorMetadata"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.benchmark_populator_metadata import (
            BenchmarkPopulatorMetadata,  # noqa: F401
        )
        # fmt: on
        populators = []
        for populators_item_data in self.populators:
            populators_item = populators_item_data.to_dict()
            populators.append(populators_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "populators": populators,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.benchmark_populator_metadata import (
            BenchmarkPopulatorMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        populators = []
        _populators = d.pop("populators")
        for populators_item_data in _populators:
            populators_item = BenchmarkPopulatorMetadata.from_dict(populators_item_data)

            populators.append(populators_item)

        obj = cls(
            populators=populators,
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
