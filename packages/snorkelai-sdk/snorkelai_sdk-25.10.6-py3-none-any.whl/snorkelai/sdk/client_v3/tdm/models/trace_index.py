from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

T = TypeVar("T", bound="TraceIndex")


@attrs.define
class TraceIndex:
    """
    Attributes:
        context_uid (Union[int, str]):
        step_id (str):
    """

    context_uid: Union[int, str]
    step_id: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        context_uid: Union[int, str]
        context_uid = self.context_uid
        step_id = self.step_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "context_uid": context_uid,
                "step_id": step_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_context_uid(data: object) -> Union[int, str]:
            return cast(Union[int, str], data)

        context_uid = _parse_context_uid(d.pop("context_uid"))

        step_id = d.pop("step_id")

        obj = cls(
            context_uid=context_uid,
            step_id=step_id,
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
