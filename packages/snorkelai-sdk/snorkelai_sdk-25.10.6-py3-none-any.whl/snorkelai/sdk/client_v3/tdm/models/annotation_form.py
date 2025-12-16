from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_schema_group import LabelSchemaGroup  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnnotationForm")


@attrs.define
class AnnotationForm:
    """
    Attributes:
        grouped_label_schemas (Union[Unset, List['LabelSchemaGroup']]): Groups of related label schemas that should be
            shown together
        individual_label_schemas (Union[Unset, List[int]]): Individual label_schema_uids not in any group
    """

    grouped_label_schemas: Union[Unset, List["LabelSchemaGroup"]] = UNSET
    individual_label_schemas: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_group import LabelSchemaGroup  # noqa: F401
        # fmt: on
        grouped_label_schemas: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.grouped_label_schemas, Unset):
            grouped_label_schemas = []
            for grouped_label_schemas_item_data in self.grouped_label_schemas:
                grouped_label_schemas_item = grouped_label_schemas_item_data.to_dict()
                grouped_label_schemas.append(grouped_label_schemas_item)

        individual_label_schemas: Union[Unset, List[int]] = UNSET
        if not isinstance(self.individual_label_schemas, Unset):
            individual_label_schemas = self.individual_label_schemas

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if grouped_label_schemas is not UNSET:
            field_dict["grouped_label_schemas"] = grouped_label_schemas
        if individual_label_schemas is not UNSET:
            field_dict["individual_label_schemas"] = individual_label_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_group import LabelSchemaGroup  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _grouped_label_schemas = d.pop("grouped_label_schemas", UNSET)
        grouped_label_schemas = []
        _grouped_label_schemas = (
            UNSET if _grouped_label_schemas is None else _grouped_label_schemas
        )
        for grouped_label_schemas_item_data in _grouped_label_schemas or []:
            grouped_label_schemas_item = LabelSchemaGroup.from_dict(
                grouped_label_schemas_item_data
            )

            grouped_label_schemas.append(grouped_label_schemas_item)

        _individual_label_schemas = d.pop("individual_label_schemas", UNSET)
        individual_label_schemas = cast(
            List[int],
            UNSET if _individual_label_schemas is None else _individual_label_schemas,
        )

        obj = cls(
            grouped_label_schemas=grouped_label_schemas,
            individual_label_schemas=individual_label_schemas,
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
