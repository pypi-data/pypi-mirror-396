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
    from ..models.copy_label_schema_payload_label_descriptions import (
        CopyLabelSchemaPayloadLabelDescriptions,  # noqa: F401
    )
    from ..models.copy_label_schema_payload_label_map import (
        CopyLabelSchemaPayloadLabelMap,  # noqa: F401
    )
    from ..models.copy_label_schema_payload_updated_label_schema import (
        CopyLabelSchemaPayloadUpdatedLabelSchema,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CopyLabelSchemaPayload")


@attrs.define
class CopyLabelSchemaPayload:
    """
    Attributes:
        name (str):
        description (Union[Unset, str]):
        label_descriptions (Union[Unset, CopyLabelSchemaPayloadLabelDescriptions]):
        label_map (Union[Unset, CopyLabelSchemaPayloadLabelMap]):
        updated_label_schema (Union[Unset, CopyLabelSchemaPayloadUpdatedLabelSchema]):
    """

    name: str
    description: Union[Unset, str] = UNSET
    label_descriptions: Union[Unset, "CopyLabelSchemaPayloadLabelDescriptions"] = UNSET
    label_map: Union[Unset, "CopyLabelSchemaPayloadLabelMap"] = UNSET
    updated_label_schema: Union[Unset, "CopyLabelSchemaPayloadUpdatedLabelSchema"] = (
        UNSET
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.copy_label_schema_payload_label_descriptions import (
            CopyLabelSchemaPayloadLabelDescriptions,  # noqa: F401
        )
        from ..models.copy_label_schema_payload_label_map import (
            CopyLabelSchemaPayloadLabelMap,  # noqa: F401
        )
        from ..models.copy_label_schema_payload_updated_label_schema import (
            CopyLabelSchemaPayloadUpdatedLabelSchema,  # noqa: F401
        )
        # fmt: on
        name = self.name
        description = self.description
        label_descriptions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_descriptions, Unset):
            label_descriptions = self.label_descriptions.to_dict()
        label_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_map, Unset):
            label_map = self.label_map.to_dict()
        updated_label_schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.updated_label_schema, Unset):
            updated_label_schema = self.updated_label_schema.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if label_descriptions is not UNSET:
            field_dict["label_descriptions"] = label_descriptions
        if label_map is not UNSET:
            field_dict["label_map"] = label_map
        if updated_label_schema is not UNSET:
            field_dict["updated_label_schema"] = updated_label_schema

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.copy_label_schema_payload_label_descriptions import (
            CopyLabelSchemaPayloadLabelDescriptions,  # noqa: F401
        )
        from ..models.copy_label_schema_payload_label_map import (
            CopyLabelSchemaPayloadLabelMap,  # noqa: F401
        )
        from ..models.copy_label_schema_payload_updated_label_schema import (
            CopyLabelSchemaPayloadUpdatedLabelSchema,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        name = d.pop("name")

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _label_descriptions = d.pop("label_descriptions", UNSET)
        _label_descriptions = (
            UNSET if _label_descriptions is None else _label_descriptions
        )
        label_descriptions: Union[Unset, CopyLabelSchemaPayloadLabelDescriptions]
        if isinstance(_label_descriptions, Unset):
            label_descriptions = UNSET
        else:
            label_descriptions = CopyLabelSchemaPayloadLabelDescriptions.from_dict(
                _label_descriptions
            )

        _label_map = d.pop("label_map", UNSET)
        _label_map = UNSET if _label_map is None else _label_map
        label_map: Union[Unset, CopyLabelSchemaPayloadLabelMap]
        if isinstance(_label_map, Unset):
            label_map = UNSET
        else:
            label_map = CopyLabelSchemaPayloadLabelMap.from_dict(_label_map)

        _updated_label_schema = d.pop("updated_label_schema", UNSET)
        _updated_label_schema = (
            UNSET if _updated_label_schema is None else _updated_label_schema
        )
        updated_label_schema: Union[Unset, CopyLabelSchemaPayloadUpdatedLabelSchema]
        if isinstance(_updated_label_schema, Unset):
            updated_label_schema = UNSET
        else:
            updated_label_schema = CopyLabelSchemaPayloadUpdatedLabelSchema.from_dict(
                _updated_label_schema
            )

        obj = cls(
            name=name,
            description=description,
            label_descriptions=label_descriptions,
            label_map=label_map,
            updated_label_schema=updated_label_schema,
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
