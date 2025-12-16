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
    from ..models.source import Source  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="GetSourcesResponse")


@attrs.define
class GetSourcesResponse:
    """
    Attributes:
        sources (List['Source']):
    """

    sources: List["Source"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.source import Source  # noqa: F401
        # fmt: on
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sources": sources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.source import Source  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = Source.from_dict(sources_item_data)

            sources.append(sources_item)

        obj = cls(
            sources=sources,
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
