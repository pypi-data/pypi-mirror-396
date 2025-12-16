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

T = TypeVar("T", bound="DataSourceUniqueColumnValuesRequest")


@attrs.define
class DataSourceUniqueColumnValuesRequest:
    """
    Attributes:
        col_name (str):
        datasource_uids (List[int]):
        application_template_id (Union[Unset, str]):
        filter_empty (Union[Unset, bool]):  Default: True.
        is_multi_label (Union[Unset, bool]):
        task_type (Union[Unset, str]):
    """

    col_name: str
    datasource_uids: List[int]
    application_template_id: Union[Unset, str] = UNSET
    filter_empty: Union[Unset, bool] = True
    is_multi_label: Union[Unset, bool] = UNSET
    task_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        col_name = self.col_name
        datasource_uids = self.datasource_uids

        application_template_id = self.application_template_id
        filter_empty = self.filter_empty
        is_multi_label = self.is_multi_label
        task_type = self.task_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "col_name": col_name,
                "datasource_uids": datasource_uids,
            }
        )
        if application_template_id is not UNSET:
            field_dict["application_template_id"] = application_template_id
        if filter_empty is not UNSET:
            field_dict["filter_empty"] = filter_empty
        if is_multi_label is not UNSET:
            field_dict["is_multi_label"] = is_multi_label
        if task_type is not UNSET:
            field_dict["task_type"] = task_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        col_name = d.pop("col_name")

        datasource_uids = cast(List[int], d.pop("datasource_uids"))

        _application_template_id = d.pop("application_template_id", UNSET)
        application_template_id = (
            UNSET if _application_template_id is None else _application_template_id
        )

        _filter_empty = d.pop("filter_empty", UNSET)
        filter_empty = UNSET if _filter_empty is None else _filter_empty

        _is_multi_label = d.pop("is_multi_label", UNSET)
        is_multi_label = UNSET if _is_multi_label is None else _is_multi_label

        _task_type = d.pop("task_type", UNSET)
        task_type = UNSET if _task_type is None else _task_type

        obj = cls(
            col_name=col_name,
            datasource_uids=datasource_uids,
            application_template_id=application_template_id,
            filter_empty=filter_empty,
            is_multi_label=is_multi_label,
            task_type=task_type,
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
