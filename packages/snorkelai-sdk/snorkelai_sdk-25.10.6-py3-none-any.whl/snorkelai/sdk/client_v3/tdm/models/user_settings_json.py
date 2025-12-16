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
    from ..models.global_preferences import GlobalPreferences  # noqa: F401
    from ..models.label_color_object import LabelColorObject  # noqa: F401
    from ..models.mta_preferences import MTAPreferences  # noqa: F401
    from ..models.user_settings_json_label_color_scheme import (
        UserSettingsJsonLabelColorScheme,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UserSettingsJson")


@attrs.define
class UserSettingsJson:
    """
    Attributes:
        custom_colors (Union[Unset, List['LabelColorObject']]):
        global_preferences (Union[Unset, GlobalPreferences]):
        label_color_scheme (Union[Unset, UserSettingsJsonLabelColorScheme]):
        mta_preferences (Union[Unset, MTAPreferences]):
        workspace_type (Union[Unset, str]):
    """

    custom_colors: Union[Unset, List["LabelColorObject"]] = UNSET
    global_preferences: Union[Unset, "GlobalPreferences"] = UNSET
    label_color_scheme: Union[Unset, "UserSettingsJsonLabelColorScheme"] = UNSET
    mta_preferences: Union[Unset, "MTAPreferences"] = UNSET
    workspace_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.global_preferences import GlobalPreferences  # noqa: F401
        from ..models.label_color_object import LabelColorObject  # noqa: F401
        from ..models.mta_preferences import MTAPreferences  # noqa: F401
        from ..models.user_settings_json_label_color_scheme import (
            UserSettingsJsonLabelColorScheme,  # noqa: F401
        )
        # fmt: on
        custom_colors: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.custom_colors, Unset):
            custom_colors = []
            for custom_colors_item_data in self.custom_colors:
                custom_colors_item = custom_colors_item_data.to_dict()
                custom_colors.append(custom_colors_item)

        global_preferences: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.global_preferences, Unset):
            global_preferences = self.global_preferences.to_dict()
        label_color_scheme: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_color_scheme, Unset):
            label_color_scheme = self.label_color_scheme.to_dict()
        mta_preferences: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.mta_preferences, Unset):
            mta_preferences = self.mta_preferences.to_dict()
        workspace_type = self.workspace_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if custom_colors is not UNSET:
            field_dict["custom_colors"] = custom_colors
        if global_preferences is not UNSET:
            field_dict["global_preferences"] = global_preferences
        if label_color_scheme is not UNSET:
            field_dict["label_color_scheme"] = label_color_scheme
        if mta_preferences is not UNSET:
            field_dict["mta_preferences"] = mta_preferences
        if workspace_type is not UNSET:
            field_dict["workspace_type"] = workspace_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.global_preferences import GlobalPreferences  # noqa: F401
        from ..models.label_color_object import LabelColorObject  # noqa: F401
        from ..models.mta_preferences import MTAPreferences  # noqa: F401
        from ..models.user_settings_json_label_color_scheme import (
            UserSettingsJsonLabelColorScheme,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _custom_colors = d.pop("custom_colors", UNSET)
        custom_colors = []
        _custom_colors = UNSET if _custom_colors is None else _custom_colors
        for custom_colors_item_data in _custom_colors or []:
            custom_colors_item = LabelColorObject.from_dict(custom_colors_item_data)

            custom_colors.append(custom_colors_item)

        _global_preferences = d.pop("global_preferences", UNSET)
        _global_preferences = (
            UNSET if _global_preferences is None else _global_preferences
        )
        global_preferences: Union[Unset, GlobalPreferences]
        if isinstance(_global_preferences, Unset):
            global_preferences = UNSET
        else:
            global_preferences = GlobalPreferences.from_dict(_global_preferences)

        _label_color_scheme = d.pop("label_color_scheme", UNSET)
        _label_color_scheme = (
            UNSET if _label_color_scheme is None else _label_color_scheme
        )
        label_color_scheme: Union[Unset, UserSettingsJsonLabelColorScheme]
        if isinstance(_label_color_scheme, Unset):
            label_color_scheme = UNSET
        else:
            label_color_scheme = UserSettingsJsonLabelColorScheme.from_dict(
                _label_color_scheme
            )

        _mta_preferences = d.pop("mta_preferences", UNSET)
        _mta_preferences = UNSET if _mta_preferences is None else _mta_preferences
        mta_preferences: Union[Unset, MTAPreferences]
        if isinstance(_mta_preferences, Unset):
            mta_preferences = UNSET
        else:
            mta_preferences = MTAPreferences.from_dict(_mta_preferences)

        _workspace_type = d.pop("workspace_type", UNSET)
        workspace_type = UNSET if _workspace_type is None else _workspace_type

        obj = cls(
            custom_colors=custom_colors,
            global_preferences=global_preferences,
            label_color_scheme=label_color_scheme,
            mta_preferences=mta_preferences,
            workspace_type=workspace_type,
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
