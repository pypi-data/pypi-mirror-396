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
    from ..models.code_evaluator import CodeEvaluator  # noqa: F401
    from ..models.code_version import CodeVersion  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="UpdateCodeEvaluatorResponse")


@attrs.define
class UpdateCodeEvaluatorResponse:
    """
    Attributes:
        code_evaluator (CodeEvaluator):
        code_version (CodeVersion):
    """

    code_evaluator: "CodeEvaluator"
    code_version: "CodeVersion"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.code_evaluator import CodeEvaluator  # noqa: F401
        from ..models.code_version import CodeVersion  # noqa: F401
        # fmt: on
        code_evaluator = self.code_evaluator.to_dict()
        code_version = self.code_version.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code_evaluator": code_evaluator,
                "code_version": code_version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.code_evaluator import CodeEvaluator  # noqa: F401
        from ..models.code_version import CodeVersion  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        code_evaluator = CodeEvaluator.from_dict(d.pop("code_evaluator"))

        code_version = CodeVersion.from_dict(d.pop("code_version"))

        obj = cls(
            code_evaluator=code_evaluator,
            code_version=code_version,
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
