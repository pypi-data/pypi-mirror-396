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
    from ..models.view_config import ViewConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="MTAPreferences")


@attrs.define
class MTAPreferences:
    """
    Attributes:
        default_multi_label_class (Union[Unset, str]):
        is_reviewer_mode (Union[Unset, bool]):
        selected_fields (Union[Unset, List[str]]):
        selected_label_schemas (Union[Unset, List[int]]):
        view_config (Union[Unset, ViewConfig]):
    """

    default_multi_label_class: Union[Unset, str] = UNSET
    is_reviewer_mode: Union[Unset, bool] = UNSET
    selected_fields: Union[Unset, List[str]] = UNSET
    selected_label_schemas: Union[Unset, List[int]] = UNSET
    view_config: Union[Unset, "ViewConfig"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.view_config import ViewConfig  # noqa: F401
        # fmt: on
        default_multi_label_class = self.default_multi_label_class
        is_reviewer_mode = self.is_reviewer_mode
        selected_fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.selected_fields, Unset):
            selected_fields = self.selected_fields

        selected_label_schemas: Union[Unset, List[int]] = UNSET
        if not isinstance(self.selected_label_schemas, Unset):
            selected_label_schemas = self.selected_label_schemas

        view_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.view_config, Unset):
            view_config = self.view_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_multi_label_class is not UNSET:
            field_dict["default_multi_label_class"] = default_multi_label_class
        if is_reviewer_mode is not UNSET:
            field_dict["is_reviewer_mode"] = is_reviewer_mode
        if selected_fields is not UNSET:
            field_dict["selected_fields"] = selected_fields
        if selected_label_schemas is not UNSET:
            field_dict["selected_label_schemas"] = selected_label_schemas
        if view_config is not UNSET:
            field_dict["view_config"] = view_config

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.view_config import ViewConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _default_multi_label_class = d.pop("default_multi_label_class", UNSET)
        default_multi_label_class = (
            UNSET if _default_multi_label_class is None else _default_multi_label_class
        )

        _is_reviewer_mode = d.pop("is_reviewer_mode", UNSET)
        is_reviewer_mode = UNSET if _is_reviewer_mode is None else _is_reviewer_mode

        _selected_fields = d.pop("selected_fields", UNSET)
        selected_fields = cast(
            List[str], UNSET if _selected_fields is None else _selected_fields
        )

        _selected_label_schemas = d.pop("selected_label_schemas", UNSET)
        selected_label_schemas = cast(
            List[int],
            UNSET if _selected_label_schemas is None else _selected_label_schemas,
        )

        _view_config = d.pop("view_config", UNSET)
        _view_config = UNSET if _view_config is None else _view_config
        view_config: Union[Unset, ViewConfig]
        if isinstance(_view_config, Unset):
            view_config = UNSET
        else:
            view_config = ViewConfig.from_dict(_view_config)

        obj = cls(
            default_multi_label_class=default_multi_label_class,
            is_reviewer_mode=is_reviewer_mode,
            selected_fields=selected_fields,
            selected_label_schemas=selected_label_schemas,
            view_config=view_config,
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
