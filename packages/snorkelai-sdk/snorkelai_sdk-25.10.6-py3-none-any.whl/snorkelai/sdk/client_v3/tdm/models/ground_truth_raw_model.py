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
    from ..models.ground_truth_raw_model_metadata import (
        GroundTruthRawModelMetadata,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GroundTruthRawModel")


@attrs.define
class GroundTruthRawModel:
    """
    Attributes:
        labels (List[Any]):
        x_uids (List[str]):
        metadata (Union[Unset, GroundTruthRawModelMetadata]):
    """

    labels: List[Any]
    x_uids: List[str]
    metadata: Union[Unset, "GroundTruthRawModelMetadata"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ground_truth_raw_model_metadata import (
            GroundTruthRawModelMetadata,  # noqa: F401
        )
        # fmt: on
        labels = self.labels

        x_uids = self.x_uids

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "labels": labels,
                "x_uids": x_uids,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ground_truth_raw_model_metadata import (
            GroundTruthRawModelMetadata,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        labels = cast(List[Any], d.pop("labels"))

        x_uids = cast(List[str], d.pop("x_uids"))

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, GroundTruthRawModelMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = GroundTruthRawModelMetadata.from_dict(_metadata)

        obj = cls(
            labels=labels,
            x_uids=x_uids,
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
