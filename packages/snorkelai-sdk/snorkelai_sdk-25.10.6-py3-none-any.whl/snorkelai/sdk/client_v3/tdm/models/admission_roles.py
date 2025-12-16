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

from ..types import UNSET, Unset

T = TypeVar("T", bound="AdmissionRoles")


@attrs.define
class AdmissionRoles:
    """
    Attributes:
        admission_roles (List[str]):
        admission_roles_claim (Union[Unset, str]):
        admission_roles_scope (Union[Unset, str]):
    """

    admission_roles: List[str]
    admission_roles_claim: Union[Unset, str] = UNSET
    admission_roles_scope: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        admission_roles = self.admission_roles

        admission_roles_claim = self.admission_roles_claim
        admission_roles_scope = self.admission_roles_scope

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "admission_roles": admission_roles,
            }
        )
        if admission_roles_claim is not UNSET:
            field_dict["admission_roles_claim"] = admission_roles_claim
        if admission_roles_scope is not UNSET:
            field_dict["admission_roles_scope"] = admission_roles_scope

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        admission_roles = cast(List[str], d.pop("admission_roles"))

        _admission_roles_claim = d.pop("admission_roles_claim", UNSET)
        admission_roles_claim = (
            UNSET if _admission_roles_claim is None else _admission_roles_claim
        )

        _admission_roles_scope = d.pop("admission_roles_scope", UNSET)
        admission_roles_scope = (
            UNSET if _admission_roles_scope is None else _admission_roles_scope
        )

        obj = cls(
            admission_roles=admission_roles,
            admission_roles_claim=admission_roles_claim,
            admission_roles_scope=admission_roles_scope,
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
