from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

T = TypeVar("T", bound="PromptDevPatchPromptRequest")


@attrs.define
class PromptDevPatchPromptRequest:
    """
    Attributes:
        prompt_version_name (str):
        starred (bool):
    """

    prompt_version_name: str
    starred: bool
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        prompt_version_name = self.prompt_version_name
        starred = self.starred

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt_version_name": prompt_version_name,
                "starred": starred,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        prompt_version_name = d.pop("prompt_version_name")

        starred = d.pop("starred")

        obj = cls(
            prompt_version_name=prompt_version_name,
            starred=starred,
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
