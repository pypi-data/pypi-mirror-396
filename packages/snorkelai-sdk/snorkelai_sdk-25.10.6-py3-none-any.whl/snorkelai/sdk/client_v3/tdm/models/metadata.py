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

from ..models.selection_strategy import SelectionStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_form import AnnotationForm  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Metadata")


@attrs.define
class Metadata:
    """
    Attributes:
        annotation_form (Union[Unset, AnnotationForm]):
        randomize (Union[Unset, bool]):
        selection_strategy (Union[Unset, SelectionStrategy]):
        source_id (Union[None, Unset, int, str]):
        source_type (Union[Unset, str]):
    """

    annotation_form: Union[Unset, "AnnotationForm"] = UNSET
    randomize: Union[Unset, bool] = UNSET
    selection_strategy: Union[Unset, SelectionStrategy] = UNSET
    source_id: Union[None, Unset, int, str] = UNSET
    source_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        # fmt: on
        annotation_form: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation_form, Unset):
            annotation_form = self.annotation_form.to_dict()
        randomize = self.randomize
        selection_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.selection_strategy, Unset):
            selection_strategy = self.selection_strategy.value

        source_id: Union[None, Unset, int, str]
        if isinstance(self.source_id, Unset):
            source_id = UNSET
        else:
            source_id = self.source_id
        source_type = self.source_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if annotation_form is not UNSET:
            field_dict["annotation_form"] = annotation_form
        if randomize is not UNSET:
            field_dict["randomize"] = randomize
        if selection_strategy is not UNSET:
            field_dict["selection_strategy"] = selection_strategy
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if source_type is not UNSET:
            field_dict["source_type"] = source_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _annotation_form = d.pop("annotation_form", UNSET)
        _annotation_form = UNSET if _annotation_form is None else _annotation_form
        annotation_form: Union[Unset, AnnotationForm]
        if isinstance(_annotation_form, Unset):
            annotation_form = UNSET
        else:
            annotation_form = AnnotationForm.from_dict(_annotation_form)

        _randomize = d.pop("randomize", UNSET)
        randomize = UNSET if _randomize is None else _randomize

        _selection_strategy = d.pop("selection_strategy", UNSET)
        _selection_strategy = (
            UNSET if _selection_strategy is None else _selection_strategy
        )
        selection_strategy: Union[Unset, SelectionStrategy]
        if isinstance(_selection_strategy, Unset):
            selection_strategy = UNSET
        else:
            selection_strategy = SelectionStrategy(_selection_strategy)

        _source_id = d.pop("source_id", UNSET)

        def _parse_source_id(data: object) -> Union[None, Unset, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int, str], data)

        source_id = _parse_source_id(UNSET if _source_id is None else _source_id)

        _source_type = d.pop("source_type", UNSET)
        source_type = UNSET if _source_type is None else _source_type

        obj = cls(
            annotation_form=annotation_form,
            randomize=randomize,
            selection_strategy=selection_strategy,
            source_id=source_id,
            source_type=source_type,
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
