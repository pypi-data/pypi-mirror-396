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
    from ..models.fetch_dataset_column_types_response_column_types import (
        FetchDatasetColumnTypesResponseColumnTypes,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="FetchDatasetColumnTypesResponse")


@attrs.define
class FetchDatasetColumnTypesResponse:
    """
    Attributes:
        column_types (FetchDatasetColumnTypesResponseColumnTypes):
    """

    column_types: "FetchDatasetColumnTypesResponseColumnTypes"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.fetch_dataset_column_types_response_column_types import (
            FetchDatasetColumnTypesResponseColumnTypes,  # noqa: F401
        )
        # fmt: on
        column_types = self.column_types.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "column_types": column_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.fetch_dataset_column_types_response_column_types import (
            FetchDatasetColumnTypesResponseColumnTypes,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        column_types = FetchDatasetColumnTypesResponseColumnTypes.from_dict(
            d.pop("column_types")
        )

        obj = cls(
            column_types=column_types,
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
