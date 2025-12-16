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
    from ..models.prompt_fm_response_data_item import (
        PromptFMResponseDataItem,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptFMResponse")


@attrs.define
class PromptFMResponse:
    """
    Attributes:
        data (Union[Unset, List['PromptFMResponseDataItem']]):
        job_id (Union[Unset, str]):
    """

    data: Union[Unset, List["PromptFMResponseDataItem"]] = UNSET
    job_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_fm_response_data_item import (
            PromptFMResponseDataItem,  # noqa: F401
        )
        # fmt: on
        data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

        job_id = self.job_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if job_id is not UNSET:
            field_dict["job_id"] = job_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_fm_response_data_item import (
            PromptFMResponseDataItem,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _data = d.pop("data", UNSET)
        data = []
        _data = UNSET if _data is None else _data
        for data_item_data in _data or []:
            data_item = PromptFMResponseDataItem.from_dict(data_item_data)

            data.append(data_item)

        _job_id = d.pop("job_id", UNSET)
        job_id = UNSET if _job_id is None else _job_id

        obj = cls(
            data=data,
            job_id=job_id,
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
