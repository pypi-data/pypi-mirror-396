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
    from ..models.label_stratification_config import (
        LabelStratificationConfig,  # noqa: F401
    )
    from ..models.single_source_config import SingleSourceConfig  # noqa: F401
    from ..models.split_by_percentage_datasource_ingestion_request_col_fill_values import (
        SplitByPercentageDatasourceIngestionRequestColFillValues,  # noqa: F401
    )
    from ..models.split_proportions import SplitProportions  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="SplitByPercentageDatasourceIngestionRequest")


@attrs.define
class SplitByPercentageDatasourceIngestionRequest:
    """
    Attributes:
        sources (List['SingleSourceConfig']): List of data sources to split
        split_proportions (SplitProportions): Distribution of data across train/valid/test splits.
        col_fill_values (Union[Unset, SplitByPercentageDatasourceIngestionRequestColFillValues]):
        label_stratification_config (Union[Unset, LabelStratificationConfig]): Parameters for ground truth
            stratification.
        load_to_model_nodes (Union[Unset, bool]): Whether to load data to model nodes Default: False.
        split_random_seed (Union[Unset, int]): Random seed for reproducible splits Default: 123.
        uid_col (Union[Unset, str]): Name of the unique ID column
    """

    sources: List["SingleSourceConfig"]
    split_proportions: "SplitProportions"
    col_fill_values: Union[
        Unset, "SplitByPercentageDatasourceIngestionRequestColFillValues"
    ] = UNSET
    label_stratification_config: Union[Unset, "LabelStratificationConfig"] = UNSET
    load_to_model_nodes: Union[Unset, bool] = False
    split_random_seed: Union[Unset, int] = 123
    uid_col: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_stratification_config import (
            LabelStratificationConfig,  # noqa: F401
        )
        from ..models.single_source_config import SingleSourceConfig  # noqa: F401
        from ..models.split_by_percentage_datasource_ingestion_request_col_fill_values import (
            SplitByPercentageDatasourceIngestionRequestColFillValues,  # noqa: F401
        )
        from ..models.split_proportions import SplitProportions  # noqa: F401
        # fmt: on
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        split_proportions = self.split_proportions.to_dict()
        col_fill_values: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.col_fill_values, Unset):
            col_fill_values = self.col_fill_values.to_dict()
        label_stratification_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_stratification_config, Unset):
            label_stratification_config = self.label_stratification_config.to_dict()
        load_to_model_nodes = self.load_to_model_nodes
        split_random_seed = self.split_random_seed
        uid_col = self.uid_col

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sources": sources,
                "split_proportions": split_proportions,
            }
        )
        if col_fill_values is not UNSET:
            field_dict["col_fill_values"] = col_fill_values
        if label_stratification_config is not UNSET:
            field_dict["label_stratification_config"] = label_stratification_config
        if load_to_model_nodes is not UNSET:
            field_dict["load_to_model_nodes"] = load_to_model_nodes
        if split_random_seed is not UNSET:
            field_dict["split_random_seed"] = split_random_seed
        if uid_col is not UNSET:
            field_dict["uid_col"] = uid_col

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_stratification_config import (
            LabelStratificationConfig,  # noqa: F401
        )
        from ..models.single_source_config import SingleSourceConfig  # noqa: F401
        from ..models.split_by_percentage_datasource_ingestion_request_col_fill_values import (
            SplitByPercentageDatasourceIngestionRequestColFillValues,  # noqa: F401
        )
        from ..models.split_proportions import SplitProportions  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = SingleSourceConfig.from_dict(sources_item_data)

            sources.append(sources_item)

        split_proportions = SplitProportions.from_dict(d.pop("split_proportions"))

        _col_fill_values = d.pop("col_fill_values", UNSET)
        _col_fill_values = UNSET if _col_fill_values is None else _col_fill_values
        col_fill_values: Union[
            Unset, SplitByPercentageDatasourceIngestionRequestColFillValues
        ]
        if isinstance(_col_fill_values, Unset):
            col_fill_values = UNSET
        else:
            col_fill_values = (
                SplitByPercentageDatasourceIngestionRequestColFillValues.from_dict(
                    _col_fill_values
                )
            )

        _label_stratification_config = d.pop("label_stratification_config", UNSET)
        _label_stratification_config = (
            UNSET
            if _label_stratification_config is None
            else _label_stratification_config
        )
        label_stratification_config: Union[Unset, LabelStratificationConfig]
        if isinstance(_label_stratification_config, Unset):
            label_stratification_config = UNSET
        else:
            label_stratification_config = LabelStratificationConfig.from_dict(
                _label_stratification_config
            )

        _load_to_model_nodes = d.pop("load_to_model_nodes", UNSET)
        load_to_model_nodes = (
            UNSET if _load_to_model_nodes is None else _load_to_model_nodes
        )

        _split_random_seed = d.pop("split_random_seed", UNSET)
        split_random_seed = UNSET if _split_random_seed is None else _split_random_seed

        _uid_col = d.pop("uid_col", UNSET)
        uid_col = UNSET if _uid_col is None else _uid_col

        obj = cls(
            sources=sources,
            split_proportions=split_proportions,
            col_fill_values=col_fill_values,
            label_stratification_config=label_stratification_config,
            load_to_model_nodes=load_to_model_nodes,
            split_random_seed=split_random_seed,
            uid_col=uid_col,
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
