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
    from ..models.update_dataset_annotation_params_metadata import (
        UpdateDatasetAnnotationParamsMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UpdateDatasetAnnotationParams")


@attrs.define
class UpdateDatasetAnnotationParams:
    """
    Attributes:
        annotation_uid (int):
        freeform_text (Union[Unset, str]):
        label (Union[Unset, Any]):
        metadata (Union[Unset, UpdateDatasetAnnotationParamsMetadata]):
    """

    annotation_uid: int
    freeform_text: Union[Unset, str] = UNSET
    label: Union[Unset, Any] = UNSET
    metadata: Union[Unset, "UpdateDatasetAnnotationParamsMetadata"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.update_dataset_annotation_params_metadata import (
            UpdateDatasetAnnotationParamsMetadata,  # noqa: F401
        )
        # fmt: on
        annotation_uid = self.annotation_uid
        freeform_text = self.freeform_text
        label = self.label
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_uid": annotation_uid,
            }
        )
        if freeform_text is not UNSET:
            field_dict["freeform_text"] = freeform_text
        if label is not UNSET:
            field_dict["label"] = label
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.update_dataset_annotation_params_metadata import (
            UpdateDatasetAnnotationParamsMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        annotation_uid = d.pop("annotation_uid")

        _freeform_text = d.pop("freeform_text", UNSET)
        freeform_text = UNSET if _freeform_text is None else _freeform_text

        _label = d.pop("label", UNSET)
        label = UNSET if _label is None else _label

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, UpdateDatasetAnnotationParamsMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateDatasetAnnotationParamsMetadata.from_dict(_metadata)

        obj = cls(
            annotation_uid=annotation_uid,
            freeform_text=freeform_text,
            label=label,
            metadata=metadata,
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
