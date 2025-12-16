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
    from ..models.data_frame_response_data_item import (
        DataFrameResponseDataItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="DataFrameResponse")


@attrs.define
class DataFrameResponse:
    """
    Attributes:
        data (List['DataFrameResponseDataItem']):
        total_count (int):
        all_x_uids (Union[Unset, List[str]]):
    """

    data: List["DataFrameResponseDataItem"]
    total_count: int
    all_x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.data_frame_response_data_item import (
            DataFrameResponseDataItem,  # noqa: F401
        )
        # fmt: on
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        total_count = self.total_count
        all_x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.all_x_uids, Unset):
            all_x_uids = self.all_x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "total_count": total_count,
            }
        )
        if all_x_uids is not UNSET:
            field_dict["all_x_uids"] = all_x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.data_frame_response_data_item import (
            DataFrameResponseDataItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = DataFrameResponseDataItem.from_dict(data_item_data)

            data.append(data_item)

        total_count = d.pop("total_count")

        _all_x_uids = d.pop("all_x_uids", UNSET)
        all_x_uids = cast(List[str], UNSET if _all_x_uids is None else _all_x_uids)

        obj = cls(
            data=data,
            total_count=total_count,
            all_x_uids=all_x_uids,
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
