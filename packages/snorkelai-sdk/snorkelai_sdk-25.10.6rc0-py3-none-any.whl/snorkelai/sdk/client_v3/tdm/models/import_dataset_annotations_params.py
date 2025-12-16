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
    from ..models.create_dataset_annotation_params import (
        CreateDatasetAnnotationParams,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ImportDatasetAnnotationsParams")


@attrs.define
class ImportDatasetAnnotationsParams:
    """
    Attributes:
        annotations (List['CreateDatasetAnnotationParams']):
        dataset_uid (int):
    """

    annotations: List["CreateDatasetAnnotationParams"]
    dataset_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_dataset_annotation_params import (
            CreateDatasetAnnotationParams,  # noqa: F401
        )
        # fmt: on
        annotations = []
        for annotations_item_data in self.annotations:
            annotations_item = annotations_item_data.to_dict()
            annotations.append(annotations_item)

        dataset_uid = self.dataset_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotations": annotations,
                "dataset_uid": dataset_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_dataset_annotation_params import (
            CreateDatasetAnnotationParams,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotations = []
        _annotations = d.pop("annotations")
        for annotations_item_data in _annotations:
            annotations_item = CreateDatasetAnnotationParams.from_dict(
                annotations_item_data
            )

            annotations.append(annotations_item)

        dataset_uid = d.pop("dataset_uid")

        obj = cls(
            annotations=annotations,
            dataset_uid=dataset_uid,
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
