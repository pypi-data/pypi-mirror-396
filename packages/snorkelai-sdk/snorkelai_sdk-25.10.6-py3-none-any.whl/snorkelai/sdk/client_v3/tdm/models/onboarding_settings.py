from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

from ..models.setup_pdf_type import SetupPDFType
from ..types import UNSET, Unset

T = TypeVar("T", bound="OnboardingSettings")


@attrs.define
class OnboardingSettings:
    """
    Attributes:
        has_user_entered_studio (Union[Unset, bool]):  Default: False.
        ie_type (Union[Unset, str]):
        image_field (Union[Unset, str]):
        pdf_type (Union[Unset, SetupPDFType]):
        pdf_url_field (Union[Unset, str]):
        primary_field (Union[Unset, str]):
    """

    has_user_entered_studio: Union[Unset, bool] = False
    ie_type: Union[Unset, str] = UNSET
    image_field: Union[Unset, str] = UNSET
    pdf_type: Union[Unset, SetupPDFType] = UNSET
    pdf_url_field: Union[Unset, str] = UNSET
    primary_field: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        has_user_entered_studio = self.has_user_entered_studio
        ie_type = self.ie_type
        image_field = self.image_field
        pdf_type: Union[Unset, str] = UNSET
        if not isinstance(self.pdf_type, Unset):
            pdf_type = self.pdf_type.value

        pdf_url_field = self.pdf_url_field
        primary_field = self.primary_field

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if has_user_entered_studio is not UNSET:
            field_dict["has_user_entered_studio"] = has_user_entered_studio
        if ie_type is not UNSET:
            field_dict["ie_type"] = ie_type
        if image_field is not UNSET:
            field_dict["image_field"] = image_field
        if pdf_type is not UNSET:
            field_dict["pdf_type"] = pdf_type
        if pdf_url_field is not UNSET:
            field_dict["pdf_url_field"] = pdf_url_field
        if primary_field is not UNSET:
            field_dict["primary_field"] = primary_field

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _has_user_entered_studio = d.pop("has_user_entered_studio", UNSET)
        has_user_entered_studio = (
            UNSET if _has_user_entered_studio is None else _has_user_entered_studio
        )

        _ie_type = d.pop("ie_type", UNSET)
        ie_type = UNSET if _ie_type is None else _ie_type

        _image_field = d.pop("image_field", UNSET)
        image_field = UNSET if _image_field is None else _image_field

        _pdf_type = d.pop("pdf_type", UNSET)
        _pdf_type = UNSET if _pdf_type is None else _pdf_type
        pdf_type: Union[Unset, SetupPDFType]
        if isinstance(_pdf_type, Unset):
            pdf_type = UNSET
        else:
            pdf_type = SetupPDFType(_pdf_type)

        _pdf_url_field = d.pop("pdf_url_field", UNSET)
        pdf_url_field = UNSET if _pdf_url_field is None else _pdf_url_field

        _primary_field = d.pop("primary_field", UNSET)
        primary_field = UNSET if _primary_field is None else _primary_field

        obj = cls(
            has_user_entered_studio=has_user_entered_studio,
            ie_type=ie_type,
            image_field=image_field,
            pdf_type=pdf_type,
            pdf_url_field=pdf_url_field,
            primary_field=primary_field,
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
