from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    cast,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.slice_template_graph_templates_item import (
        SliceTemplateGraphTemplatesItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="SliceTemplateGraph")


@attrs.define
class SliceTemplateGraph:
    """
    Attributes:
        graph (List[Any]):
        templates (List['SliceTemplateGraphTemplatesItem']):
    """

    graph: List[Any]
    templates: List["SliceTemplateGraphTemplatesItem"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.slice_template_graph_templates_item import (
            SliceTemplateGraphTemplatesItem,  # noqa: F401
        )
        # fmt: on
        graph = self.graph

        templates = []
        for templates_item_data in self.templates:
            templates_item = templates_item_data.to_dict()
            templates.append(templates_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "graph": graph,
                "templates": templates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.slice_template_graph_templates_item import (
            SliceTemplateGraphTemplatesItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        graph = cast(List[Any], d.pop("graph"))

        templates = []
        _templates = d.pop("templates")
        for templates_item_data in _templates:
            templates_item = SliceTemplateGraphTemplatesItem.from_dict(
                templates_item_data
            )

            templates.append(templates_item)

        obj = cls(
            graph=graph,
            templates=templates,
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
