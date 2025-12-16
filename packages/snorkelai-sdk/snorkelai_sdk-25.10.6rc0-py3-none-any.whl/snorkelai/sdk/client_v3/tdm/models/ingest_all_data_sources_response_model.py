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
    from ..models.ingest_all_data_sources_response_model_splitwise_response_item import (
        IngestAllDataSourcesResponseModelSplitwiseResponseItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="IngestAllDataSourcesResponseModel")


@attrs.define
class IngestAllDataSourcesResponseModel:
    """
    Attributes:
        splitwise_response (List['IngestAllDataSourcesResponseModelSplitwiseResponseItem']):
    """

    splitwise_response: List["IngestAllDataSourcesResponseModelSplitwiseResponseItem"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ingest_all_data_sources_response_model_splitwise_response_item import (
            IngestAllDataSourcesResponseModelSplitwiseResponseItem,  # noqa: F401
        )
        # fmt: on
        splitwise_response = []
        for splitwise_response_item_data in self.splitwise_response:
            splitwise_response_item = splitwise_response_item_data.to_dict()
            splitwise_response.append(splitwise_response_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "splitwise_response": splitwise_response,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ingest_all_data_sources_response_model_splitwise_response_item import (
            IngestAllDataSourcesResponseModelSplitwiseResponseItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        splitwise_response = []
        _splitwise_response = d.pop("splitwise_response")
        for splitwise_response_item_data in _splitwise_response:
            splitwise_response_item = (
                IngestAllDataSourcesResponseModelSplitwiseResponseItem.from_dict(
                    splitwise_response_item_data
                )
            )

            splitwise_response.append(splitwise_response_item)

        obj = cls(
            splitwise_response=splitwise_response,
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
