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
    from ..models.import_dataset_annotations_response_object import (
        ImportDatasetAnnotationsResponseObject,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ImportDatasetAnnotationsResponse")


@attrs.define
class ImportDatasetAnnotationsResponse:
    """
    Attributes:
        created_annotations (List['ImportDatasetAnnotationsResponseObject']):
    """

    created_annotations: List["ImportDatasetAnnotationsResponseObject"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.import_dataset_annotations_response_object import (
            ImportDatasetAnnotationsResponseObject,  # noqa: F401
        )
        # fmt: on
        created_annotations = []
        for created_annotations_item_data in self.created_annotations:
            created_annotations_item = created_annotations_item_data.to_dict()
            created_annotations.append(created_annotations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_annotations": created_annotations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.import_dataset_annotations_response_object import (
            ImportDatasetAnnotationsResponseObject,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        created_annotations = []
        _created_annotations = d.pop("created_annotations")
        for created_annotations_item_data in _created_annotations:
            created_annotations_item = ImportDatasetAnnotationsResponseObject.from_dict(
                created_annotations_item_data
            )

            created_annotations.append(created_annotations_item)

        obj = cls(
            created_annotations=created_annotations,
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
