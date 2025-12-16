from typing import (
    Any,
    Dict,
    List,
    Literal,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.filter_transform_filter_types import FilterTransformFilterTypes
from ..types import UNSET, Unset

T = TypeVar("T", bound="MarginDistanceFilterSchema")


@attrs.define
class MarginDistanceFilterSchema:
    """
    Attributes:
        margin_distance (float):
        model_uid (int):
        most_confident_prediction (str):
        second_most_confident_prediction (str):
        filter_type (Union[Unset, FilterTransformFilterTypes]):
        transform_config_type (Union[Literal['margin_distance_filter_schema'], Unset]):  Default:
            'margin_distance_filter_schema'.
    """

    margin_distance: float
    model_uid: int
    most_confident_prediction: str
    second_most_confident_prediction: str
    filter_type: Union[Unset, FilterTransformFilterTypes] = UNSET
    transform_config_type: Union[Literal["margin_distance_filter_schema"], Unset] = (
        "margin_distance_filter_schema"
    )
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        margin_distance = self.margin_distance
        model_uid = self.model_uid
        most_confident_prediction = self.most_confident_prediction
        second_most_confident_prediction = self.second_most_confident_prediction
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        transform_config_type = self.transform_config_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "margin_distance": margin_distance,
                "model_uid": model_uid,
                "most_confident_prediction": most_confident_prediction,
                "second_most_confident_prediction": second_most_confident_prediction,
            }
        )
        if filter_type is not UNSET:
            field_dict["filter_type"] = filter_type
        if transform_config_type is not UNSET:
            field_dict["transform_config_type"] = transform_config_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        margin_distance = d.pop("margin_distance")

        model_uid = d.pop("model_uid")

        most_confident_prediction = d.pop("most_confident_prediction")

        second_most_confident_prediction = d.pop("second_most_confident_prediction")

        _filter_type = d.pop("filter_type", UNSET)
        _filter_type = UNSET if _filter_type is None else _filter_type
        filter_type: Union[Unset, FilterTransformFilterTypes]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = FilterTransformFilterTypes(_filter_type)

        _transform_config_type = d.pop("transform_config_type", UNSET)
        transform_config_type = (
            UNSET if _transform_config_type is None else _transform_config_type
        )

        obj = cls(
            margin_distance=margin_distance,
            model_uid=model_uid,
            most_confident_prediction=most_confident_prediction,
            second_most_confident_prediction=second_most_confident_prediction,
            filter_type=filter_type,
            transform_config_type=transform_config_type,
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
