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
    from ..models.ingest_single_datasource_response_datasource import (
        IngestSingleDatasourceResponseDatasource,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="IngestSingleDatasourceResponse")


@attrs.define
class IngestSingleDatasourceResponse:
    """Response for data ingestion operations.

    Attributes:
        job_id (str):
        dataset_uid (Union[Unset, int]):
        datasource (Union[Unset, IngestSingleDatasourceResponseDatasource]):
    """

    job_id: str
    dataset_uid: Union[Unset, int] = UNSET
    datasource: Union[Unset, "IngestSingleDatasourceResponseDatasource"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ingest_single_datasource_response_datasource import (
            IngestSingleDatasourceResponseDatasource,  # noqa: F401
        )
        # fmt: on
        job_id = self.job_id
        dataset_uid = self.dataset_uid
        datasource: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.datasource, Unset):
            datasource = self.datasource.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
            }
        )
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if datasource is not UNSET:
            field_dict["datasource"] = datasource

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ingest_single_datasource_response_datasource import (
            IngestSingleDatasourceResponseDatasource,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        job_id = d.pop("job_id")

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _datasource = d.pop("datasource", UNSET)
        _datasource = UNSET if _datasource is None else _datasource
        datasource: Union[Unset, IngestSingleDatasourceResponseDatasource]
        if isinstance(_datasource, Unset):
            datasource = UNSET
        else:
            datasource = IngestSingleDatasourceResponseDatasource.from_dict(_datasource)

        obj = cls(
            job_id=job_id,
            dataset_uid=dataset_uid,
            datasource=datasource,
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
