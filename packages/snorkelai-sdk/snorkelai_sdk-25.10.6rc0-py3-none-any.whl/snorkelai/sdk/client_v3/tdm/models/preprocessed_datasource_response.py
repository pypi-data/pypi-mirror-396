import datetime
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
from dateutil.parser import isoparse

from ..models.datasource_role import DatasourceRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.load_config import LoadConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PreprocessedDatasourceResponse")


@attrs.define
class PreprocessedDatasourceResponse:
    """
    Attributes:
        config (LoadConfig):
        datasource_uid (int):
        ds (datetime.date):
        ds_role (DatasourceRole):
        is_active (bool):
        split (str):
        supports_dev (bool):
        type (int):
        bumped_ops_and_preprocessed_version (Union[Unset, List[List[Union[int, str]]]]):
        is_purely_op_impl_version_mismatch (Union[Unset, bool]):
        is_stale (Union[Unset, bool]):
        n_datapoints (Union[Unset, int]):
        n_docs (Union[Unset, int]):
        n_gt_labels (Union[Unset, int]):
        stale_reasons (Union[Unset, List[str]]):
    """

    config: "LoadConfig"
    datasource_uid: int
    ds: datetime.date
    ds_role: DatasourceRole
    is_active: bool
    split: str
    supports_dev: bool
    type: int
    bumped_ops_and_preprocessed_version: Union[Unset, List[List[Union[int, str]]]] = (
        UNSET
    )
    is_purely_op_impl_version_mismatch: Union[Unset, bool] = UNSET
    is_stale: Union[Unset, bool] = UNSET
    n_datapoints: Union[Unset, int] = UNSET
    n_docs: Union[Unset, int] = UNSET
    n_gt_labels: Union[Unset, int] = UNSET
    stale_reasons: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.load_config import LoadConfig  # noqa: F401
        # fmt: on
        config = self.config.to_dict()
        datasource_uid = self.datasource_uid
        ds = self.ds.isoformat()
        ds_role = self.ds_role.value
        is_active = self.is_active
        split = self.split
        supports_dev = self.supports_dev
        type = self.type
        bumped_ops_and_preprocessed_version: Union[
            Unset, List[List[Union[int, str]]]
        ] = UNSET
        if not isinstance(self.bumped_ops_and_preprocessed_version, Unset):
            bumped_ops_and_preprocessed_version = []
            for (
                bumped_ops_and_preprocessed_version_item_data
            ) in self.bumped_ops_and_preprocessed_version:
                bumped_ops_and_preprocessed_version_item = []
                for (
                    bumped_ops_and_preprocessed_version_item_item_data
                ) in bumped_ops_and_preprocessed_version_item_data:
                    bumped_ops_and_preprocessed_version_item_item: Union[int, str]
                    bumped_ops_and_preprocessed_version_item_item = (
                        bumped_ops_and_preprocessed_version_item_item_data
                    )
                    bumped_ops_and_preprocessed_version_item.append(
                        bumped_ops_and_preprocessed_version_item_item
                    )

                bumped_ops_and_preprocessed_version.append(
                    bumped_ops_and_preprocessed_version_item
                )

        is_purely_op_impl_version_mismatch = self.is_purely_op_impl_version_mismatch
        is_stale = self.is_stale
        n_datapoints = self.n_datapoints
        n_docs = self.n_docs
        n_gt_labels = self.n_gt_labels
        stale_reasons: Union[Unset, List[str]] = UNSET
        if not isinstance(self.stale_reasons, Unset):
            stale_reasons = self.stale_reasons

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "datasource_uid": datasource_uid,
                "ds": ds,
                "ds_role": ds_role,
                "is_active": is_active,
                "split": split,
                "supports_dev": supports_dev,
                "type": type,
            }
        )
        if bumped_ops_and_preprocessed_version is not UNSET:
            field_dict["bumped_ops_and_preprocessed_version"] = (
                bumped_ops_and_preprocessed_version
            )
        if is_purely_op_impl_version_mismatch is not UNSET:
            field_dict["is_purely_op_impl_version_mismatch"] = (
                is_purely_op_impl_version_mismatch
            )
        if is_stale is not UNSET:
            field_dict["is_stale"] = is_stale
        if n_datapoints is not UNSET:
            field_dict["n_datapoints"] = n_datapoints
        if n_docs is not UNSET:
            field_dict["n_docs"] = n_docs
        if n_gt_labels is not UNSET:
            field_dict["n_gt_labels"] = n_gt_labels
        if stale_reasons is not UNSET:
            field_dict["stale_reasons"] = stale_reasons

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.load_config import LoadConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        config = LoadConfig.from_dict(d.pop("config"))

        datasource_uid = d.pop("datasource_uid")

        ds = isoparse(d.pop("ds")).date()

        ds_role = DatasourceRole(d.pop("ds_role"))

        is_active = d.pop("is_active")

        split = d.pop("split")

        supports_dev = d.pop("supports_dev")

        type = d.pop("type")

        _bumped_ops_and_preprocessed_version = d.pop(
            "bumped_ops_and_preprocessed_version", UNSET
        )
        bumped_ops_and_preprocessed_version = []
        _bumped_ops_and_preprocessed_version = (
            UNSET
            if _bumped_ops_and_preprocessed_version is None
            else _bumped_ops_and_preprocessed_version
        )
        for bumped_ops_and_preprocessed_version_item_data in (
            _bumped_ops_and_preprocessed_version or []
        ):
            bumped_ops_and_preprocessed_version_item = []
            _bumped_ops_and_preprocessed_version_item = (
                bumped_ops_and_preprocessed_version_item_data
            )
            for (
                bumped_ops_and_preprocessed_version_item_item_data
            ) in _bumped_ops_and_preprocessed_version_item:

                def _parse_bumped_ops_and_preprocessed_version_item_item(
                    data: object,
                ) -> Union[int, str]:
                    return cast(Union[int, str], data)

                bumped_ops_and_preprocessed_version_item_item = (
                    _parse_bumped_ops_and_preprocessed_version_item_item(
                        bumped_ops_and_preprocessed_version_item_item_data
                    )
                )

                bumped_ops_and_preprocessed_version_item.append(
                    bumped_ops_and_preprocessed_version_item_item
                )

            bumped_ops_and_preprocessed_version.append(
                bumped_ops_and_preprocessed_version_item
            )

        _is_purely_op_impl_version_mismatch = d.pop(
            "is_purely_op_impl_version_mismatch", UNSET
        )
        is_purely_op_impl_version_mismatch = (
            UNSET
            if _is_purely_op_impl_version_mismatch is None
            else _is_purely_op_impl_version_mismatch
        )

        _is_stale = d.pop("is_stale", UNSET)
        is_stale = UNSET if _is_stale is None else _is_stale

        _n_datapoints = d.pop("n_datapoints", UNSET)
        n_datapoints = UNSET if _n_datapoints is None else _n_datapoints

        _n_docs = d.pop("n_docs", UNSET)
        n_docs = UNSET if _n_docs is None else _n_docs

        _n_gt_labels = d.pop("n_gt_labels", UNSET)
        n_gt_labels = UNSET if _n_gt_labels is None else _n_gt_labels

        _stale_reasons = d.pop("stale_reasons", UNSET)
        stale_reasons = cast(
            List[str], UNSET if _stale_reasons is None else _stale_reasons
        )

        obj = cls(
            config=config,
            datasource_uid=datasource_uid,
            ds=ds,
            ds_role=ds_role,
            is_active=is_active,
            split=split,
            supports_dev=supports_dev,
            type=type,
            bumped_ops_and_preprocessed_version=bumped_ops_and_preprocessed_version,
            is_purely_op_impl_version_mismatch=is_purely_op_impl_version_mismatch,
            is_stale=is_stale,
            n_datapoints=n_datapoints,
            n_docs=n_docs,
            n_gt_labels=n_gt_labels,
            stale_reasons=stale_reasons,
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
