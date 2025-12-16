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
    from ..models.option_model import OptionModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LabelSchemaFilterStructureModel")


@attrs.define
class LabelSchemaFilterStructureModel:
    """
    Attributes:
        id (List[int]):
        name (str):
        voted_options (List['OptionModel']):
        vote_type_options (Union[Unset, List['OptionModel']]):
    """

    id: List[int]
    name: str
    voted_options: List["OptionModel"]
    vote_type_options: Union[Unset, List["OptionModel"]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        id = self.id

        name = self.name
        voted_options = []
        for voted_options_item_data in self.voted_options:
            voted_options_item = voted_options_item_data.to_dict()
            voted_options.append(voted_options_item)

        vote_type_options: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.vote_type_options, Unset):
            vote_type_options = []
            for vote_type_options_item_data in self.vote_type_options:
                vote_type_options_item = vote_type_options_item_data.to_dict()
                vote_type_options.append(vote_type_options_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "voted_options": voted_options,
            }
        )
        if vote_type_options is not UNSET:
            field_dict["vote_type_options"] = vote_type_options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        id = cast(List[int], d.pop("id"))

        name = d.pop("name")

        voted_options = []
        _voted_options = d.pop("voted_options")
        for voted_options_item_data in _voted_options:
            voted_options_item = OptionModel.from_dict(voted_options_item_data)

            voted_options.append(voted_options_item)

        _vote_type_options = d.pop("vote_type_options", UNSET)
        vote_type_options = []
        _vote_type_options = UNSET if _vote_type_options is None else _vote_type_options
        for vote_type_options_item_data in _vote_type_options or []:
            vote_type_options_item = OptionModel.from_dict(vote_type_options_item_data)

            vote_type_options.append(vote_type_options_item)

        obj = cls(
            id=id,
            name=name,
            voted_options=voted_options,
            vote_type_options=vote_type_options,
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
