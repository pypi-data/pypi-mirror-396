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

if TYPE_CHECKING:
    # fmt: off
    from ..models.remote_static_asset_upload_request import (
        RemoteStaticAssetUploadRequest,  # noqa: F401
    )
    from ..models.split_by_file_datasource_ingestion_request import (
        SplitByFileDatasourceIngestionRequest,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="UnifiedIngestDatasourcesRequest")


@attrs.define
class UnifiedIngestDatasourcesRequest:
    """Request model for ingesting one or more data sources with explicit splits.

    Attributes:
        datasources (List[Union['RemoteStaticAssetUploadRequest', 'SplitByFileDatasourceIngestionRequest']]):
    """

    datasources: List[
        Union["RemoteStaticAssetUploadRequest", "SplitByFileDatasourceIngestionRequest"]
    ]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.remote_static_asset_upload_request import (
            RemoteStaticAssetUploadRequest,  # noqa: F401
        )
        from ..models.split_by_file_datasource_ingestion_request import (
            SplitByFileDatasourceIngestionRequest,  # noqa: F401
        )
        # fmt: on
        datasources = []
        for datasources_item_data in self.datasources:
            datasources_item: Dict[str, Any]
            if isinstance(datasources_item_data, SplitByFileDatasourceIngestionRequest):
                datasources_item = datasources_item_data.to_dict()
            else:
                datasources_item = datasources_item_data.to_dict()

            datasources.append(datasources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "datasources": datasources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.remote_static_asset_upload_request import (
            RemoteStaticAssetUploadRequest,  # noqa: F401
        )
        from ..models.split_by_file_datasource_ingestion_request import (
            SplitByFileDatasourceIngestionRequest,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        datasources = []
        _datasources = d.pop("datasources")
        for datasources_item_data in _datasources:

            def _parse_datasources_item(
                data: object,
            ) -> Union[
                "RemoteStaticAssetUploadRequest",
                "SplitByFileDatasourceIngestionRequest",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    datasources_item_type_0 = (
                        SplitByFileDatasourceIngestionRequest.from_dict(data)
                    )

                    return datasources_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                datasources_item_type_1 = RemoteStaticAssetUploadRequest.from_dict(data)

                return datasources_item_type_1

            datasources_item = _parse_datasources_item(datasources_item_data)

            datasources.append(datasources_item)

        obj = cls(
            datasources=datasources,
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
