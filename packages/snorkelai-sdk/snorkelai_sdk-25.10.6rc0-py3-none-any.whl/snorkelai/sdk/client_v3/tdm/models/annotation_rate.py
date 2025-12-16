import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs
from dateutil.parser import isoparse

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_rate_data import AnnotationRateData  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnnotationRate")


@attrs.define
class AnnotationRate:
    """
    Attributes:
        data (List['AnnotationRateData']):
        end_time (datetime.datetime):
        start_time (datetime.datetime):
    """

    data: List["AnnotationRateData"]
    end_time: datetime.datetime
    start_time: datetime.datetime
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_rate_data import AnnotationRateData  # noqa: F401
        # fmt: on
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        end_time = self.end_time.isoformat()
        start_time = self.start_time.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "end_time": end_time,
                "start_time": start_time,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_rate_data import AnnotationRateData  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = AnnotationRateData.from_dict(data_item_data)

            data.append(data_item)

        end_time = isoparse(d.pop("end_time"))

        start_time = isoparse(d.pop("start_time"))

        obj = cls(
            data=data,
            end_time=end_time,
            start_time=start_time,
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
