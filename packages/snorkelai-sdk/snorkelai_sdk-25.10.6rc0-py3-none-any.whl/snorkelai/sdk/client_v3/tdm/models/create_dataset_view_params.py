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

from ..models.dataset_view_types import DatasetViewTypes
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.create_dataset_view_params_column_mapping import (
        CreateDatasetViewParamsColumnMapping,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="CreateDatasetViewParams")


@attrs.define
class CreateDatasetViewParams:
    """
    Attributes:
        column_mapping (CreateDatasetViewParamsColumnMapping):
        dataset_uid (int):
        name (str):
        view_type (DatasetViewTypes):
        label_schema_uids (Union[Unset, List[int]]):
    """

    column_mapping: "CreateDatasetViewParamsColumnMapping"
    dataset_uid: int
    name: str
    view_type: DatasetViewTypes
    label_schema_uids: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_dataset_view_params_column_mapping import (
            CreateDatasetViewParamsColumnMapping,  # noqa: F401
        )
        # fmt: on
        column_mapping = self.column_mapping.to_dict()
        dataset_uid = self.dataset_uid
        name = self.name
        view_type = self.view_type.value
        label_schema_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.label_schema_uids, Unset):
            label_schema_uids = self.label_schema_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "column_mapping": column_mapping,
                "dataset_uid": dataset_uid,
                "name": name,
                "view_type": view_type,
            }
        )
        if label_schema_uids is not UNSET:
            field_dict["label_schema_uids"] = label_schema_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_dataset_view_params_column_mapping import (
            CreateDatasetViewParamsColumnMapping,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        column_mapping = CreateDatasetViewParamsColumnMapping.from_dict(
            d.pop("column_mapping")
        )

        dataset_uid = d.pop("dataset_uid")

        name = d.pop("name")

        view_type = DatasetViewTypes(d.pop("view_type"))

        _label_schema_uids = d.pop("label_schema_uids", UNSET)
        label_schema_uids = cast(
            List[int], UNSET if _label_schema_uids is None else _label_schema_uids
        )

        obj = cls(
            column_mapping=column_mapping,
            dataset_uid=dataset_uid,
            name=name,
            view_type=view_type,
            label_schema_uids=label_schema_uids,
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
