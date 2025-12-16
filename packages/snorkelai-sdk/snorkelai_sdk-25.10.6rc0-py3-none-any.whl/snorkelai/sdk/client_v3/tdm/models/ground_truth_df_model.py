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
    from ..models.ground_truth_df_model_label_map import (
        GroundTruthDFModelLabelMap,  # noqa: F401
    )
    from ..models.ground_truth_df_model_remap_labels import (
        GroundTruthDFModelRemapLabels,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="GroundTruthDFModel")


@attrs.define
class GroundTruthDFModel:
    """
    Attributes:
        serialized_df (str):
        label_col (Union[Unset, str]):  Default: 'label'.
        label_map (Union[Unset, GroundTruthDFModelLabelMap]):
        remap_labels (Union[Unset, GroundTruthDFModelRemapLabels]):
    """

    serialized_df: str
    label_col: Union[Unset, str] = "label"
    label_map: Union[Unset, "GroundTruthDFModelLabelMap"] = UNSET
    remap_labels: Union[Unset, "GroundTruthDFModelRemapLabels"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ground_truth_df_model_label_map import (
            GroundTruthDFModelLabelMap,  # noqa: F401
        )
        from ..models.ground_truth_df_model_remap_labels import (
            GroundTruthDFModelRemapLabels,  # noqa: F401
        )
        # fmt: on
        serialized_df = self.serialized_df
        label_col = self.label_col
        label_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_map, Unset):
            label_map = self.label_map.to_dict()
        remap_labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.remap_labels, Unset):
            remap_labels = self.remap_labels.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "serialized_df": serialized_df,
            }
        )
        if label_col is not UNSET:
            field_dict["label_col"] = label_col
        if label_map is not UNSET:
            field_dict["label_map"] = label_map
        if remap_labels is not UNSET:
            field_dict["remap_labels"] = remap_labels

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ground_truth_df_model_label_map import (
            GroundTruthDFModelLabelMap,  # noqa: F401
        )
        from ..models.ground_truth_df_model_remap_labels import (
            GroundTruthDFModelRemapLabels,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        serialized_df = d.pop("serialized_df")

        _label_col = d.pop("label_col", UNSET)
        label_col = UNSET if _label_col is None else _label_col

        _label_map = d.pop("label_map", UNSET)
        _label_map = UNSET if _label_map is None else _label_map
        label_map: Union[Unset, GroundTruthDFModelLabelMap]
        if isinstance(_label_map, Unset):
            label_map = UNSET
        else:
            label_map = GroundTruthDFModelLabelMap.from_dict(_label_map)

        _remap_labels = d.pop("remap_labels", UNSET)
        _remap_labels = UNSET if _remap_labels is None else _remap_labels
        remap_labels: Union[Unset, GroundTruthDFModelRemapLabels]
        if isinstance(_remap_labels, Unset):
            remap_labels = UNSET
        else:
            remap_labels = GroundTruthDFModelRemapLabels.from_dict(_remap_labels)

        obj = cls(
            serialized_df=serialized_df,
            label_col=label_col,
            label_map=label_map,
            remap_labels=remap_labels,
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
