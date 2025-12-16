from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_space_config_kwargs import LabelSpaceConfigKwargs  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LabelSpaceConfig")


@attrs.define
class LabelSpaceConfig:
    """
    Attributes:
        cls_name (str):
        kwargs (LabelSpaceConfigKwargs):
    """

    cls_name: str
    kwargs: "LabelSpaceConfigKwargs"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_space_config_kwargs import (
            LabelSpaceConfigKwargs,  # noqa: F401
        )
        # fmt: on
        cls_name = self.cls_name
        kwargs = self.kwargs.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cls_name": cls_name,
                "kwargs": kwargs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_space_config_kwargs import (
            LabelSpaceConfigKwargs,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        cls_name = d.pop("cls_name")

        kwargs = LabelSpaceConfigKwargs.from_dict(d.pop("kwargs"))

        obj = cls(
            cls_name=cls_name,
            kwargs=kwargs,
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
