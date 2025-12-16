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
    from ..models.prompt_template_with_metadata import (
        PromptTemplateWithMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptTemplatesListResponse")


@attrs.define
class PromptTemplatesListResponse:
    """
    Attributes:
        limit (int):
        offset (int):
        templates (List['PromptTemplateWithMetadata']):
        total_count (int):
    """

    limit: int
    offset: int
    templates: List["PromptTemplateWithMetadata"]
    total_count: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_template_with_metadata import (
            PromptTemplateWithMetadata,  # noqa: F401
        )
        # fmt: on
        limit = self.limit
        offset = self.offset
        templates = []
        for templates_item_data in self.templates:
            templates_item = templates_item_data.to_dict()
            templates.append(templates_item)

        total_count = self.total_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "limit": limit,
                "offset": offset,
                "templates": templates,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_template_with_metadata import (
            PromptTemplateWithMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        limit = d.pop("limit")

        offset = d.pop("offset")

        templates = []
        _templates = d.pop("templates")
        for templates_item_data in _templates:
            templates_item = PromptTemplateWithMetadata.from_dict(templates_item_data)

            templates.append(templates_item)

        total_count = d.pop("total_count")

        obj = cls(
            limit=limit,
            offset=offset,
            templates=templates,
            total_count=total_count,
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
