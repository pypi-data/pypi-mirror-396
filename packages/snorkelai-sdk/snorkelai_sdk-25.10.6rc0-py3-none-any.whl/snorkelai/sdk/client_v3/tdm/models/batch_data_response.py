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
    from ..models.annotation_form import AnnotationForm  # noqa: F401
    from ..models.batch_data_response_data_item import (
        BatchDataResponseDataItem,  # noqa: F401
    )
    from ..models.batch_data_response_field_docstrings import (
        BatchDataResponseFieldDocstrings,  # noqa: F401
    )
    from ..models.batch_data_response_grouped_data import (
        BatchDataResponseGroupedData,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="BatchDataResponse")


@attrs.define
class BatchDataResponse:
    """
    Attributes:
        count (int):
        data (List['BatchDataResponseDataItem']):
        field_docstrings (BatchDataResponseFieldDocstrings):
        field_types (List[str]):
        fields (List[str]):
        offset (int):
        rich_doc_field (str):
        total_count (int):
        total_index (List[str]):
        uid_field (str):
        annotation_form (Union[Unset, AnnotationForm]):
        context_uid_field (Union[Unset, str]):
        context_x_uid_field (Union[Unset, str]):
        grouped_data (Union[Unset, BatchDataResponseGroupedData]):
    """

    count: int
    data: List["BatchDataResponseDataItem"]
    field_docstrings: "BatchDataResponseFieldDocstrings"
    field_types: List[str]
    fields: List[str]
    offset: int
    rich_doc_field: str
    total_count: int
    total_index: List[str]
    uid_field: str
    annotation_form: Union[Unset, "AnnotationForm"] = UNSET
    context_uid_field: Union[Unset, str] = UNSET
    context_x_uid_field: Union[Unset, str] = UNSET
    grouped_data: Union[Unset, "BatchDataResponseGroupedData"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.batch_data_response_data_item import (
            BatchDataResponseDataItem,  # noqa: F401
        )
        from ..models.batch_data_response_field_docstrings import (
            BatchDataResponseFieldDocstrings,  # noqa: F401
        )
        from ..models.batch_data_response_grouped_data import (
            BatchDataResponseGroupedData,  # noqa: F401
        )
        # fmt: on
        count = self.count
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        field_docstrings = self.field_docstrings.to_dict()
        field_types = self.field_types

        fields = self.fields

        offset = self.offset
        rich_doc_field = self.rich_doc_field
        total_count = self.total_count
        total_index = self.total_index

        uid_field = self.uid_field
        annotation_form: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation_form, Unset):
            annotation_form = self.annotation_form.to_dict()
        context_uid_field = self.context_uid_field
        context_x_uid_field = self.context_x_uid_field
        grouped_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.grouped_data, Unset):
            grouped_data = self.grouped_data.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "data": data,
                "field_docstrings": field_docstrings,
                "field_types": field_types,
                "fields": fields,
                "offset": offset,
                "rich_doc_field": rich_doc_field,
                "total_count": total_count,
                "total_index": total_index,
                "uid_field": uid_field,
            }
        )
        if annotation_form is not UNSET:
            field_dict["annotation_form"] = annotation_form
        if context_uid_field is not UNSET:
            field_dict["context_uid_field"] = context_uid_field
        if context_x_uid_field is not UNSET:
            field_dict["context_x_uid_field"] = context_x_uid_field
        if grouped_data is not UNSET:
            field_dict["grouped_data"] = grouped_data

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.batch_data_response_data_item import (
            BatchDataResponseDataItem,  # noqa: F401
        )
        from ..models.batch_data_response_field_docstrings import (
            BatchDataResponseFieldDocstrings,  # noqa: F401
        )
        from ..models.batch_data_response_grouped_data import (
            BatchDataResponseGroupedData,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        count = d.pop("count")

        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = BatchDataResponseDataItem.from_dict(data_item_data)

            data.append(data_item)

        field_docstrings = BatchDataResponseFieldDocstrings.from_dict(
            d.pop("field_docstrings")
        )

        field_types = cast(List[str], d.pop("field_types"))

        fields = cast(List[str], d.pop("fields"))

        offset = d.pop("offset")

        rich_doc_field = d.pop("rich_doc_field")

        total_count = d.pop("total_count")

        total_index = cast(List[str], d.pop("total_index"))

        uid_field = d.pop("uid_field")

        _annotation_form = d.pop("annotation_form", UNSET)
        _annotation_form = UNSET if _annotation_form is None else _annotation_form
        annotation_form: Union[Unset, AnnotationForm]
        if isinstance(_annotation_form, Unset):
            annotation_form = UNSET
        else:
            annotation_form = AnnotationForm.from_dict(_annotation_form)

        _context_uid_field = d.pop("context_uid_field", UNSET)
        context_uid_field = UNSET if _context_uid_field is None else _context_uid_field

        _context_x_uid_field = d.pop("context_x_uid_field", UNSET)
        context_x_uid_field = (
            UNSET if _context_x_uid_field is None else _context_x_uid_field
        )

        _grouped_data = d.pop("grouped_data", UNSET)
        _grouped_data = UNSET if _grouped_data is None else _grouped_data
        grouped_data: Union[Unset, BatchDataResponseGroupedData]
        if isinstance(_grouped_data, Unset):
            grouped_data = UNSET
        else:
            grouped_data = BatchDataResponseGroupedData.from_dict(_grouped_data)

        obj = cls(
            count=count,
            data=data,
            field_docstrings=field_docstrings,
            field_types=field_types,
            fields=fields,
            offset=offset,
            rich_doc_field=rich_doc_field,
            total_count=total_count,
            total_index=total_index,
            uid_field=uid_field,
            annotation_form=annotation_form,
            context_uid_field=context_uid_field,
            context_x_uid_field=context_x_uid_field,
            grouped_data=grouped_data,
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
