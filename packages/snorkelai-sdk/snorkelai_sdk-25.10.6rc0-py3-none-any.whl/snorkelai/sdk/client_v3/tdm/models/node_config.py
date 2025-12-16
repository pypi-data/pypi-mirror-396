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

from ..models.candidate_ie_type import CandidateIEType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_space_config import LabelSpaceConfig  # noqa: F401
    from ..models.node_config_columns_metadata import (
        NodeConfigColumnsMetadata,  # noqa: F401
    )
    from ..models.node_config_gt_parent_version_map import (
        NodeConfigGtParentVersionMap,  # noqa: F401
    )
    from ..models.node_config_label_map import NodeConfigLabelMap  # noqa: F401
    from ..models.node_config_label_space_config_type_0 import (
        NodeConfigLabelSpaceConfigType0,  # noqa: F401
    )
    from ..models.node_config_misc_node_info import NodeConfigMiscNodeInfo  # noqa: F401
    from ..models.node_config_special_columns import (
        NodeConfigSpecialColumns,  # noqa: F401
    )
    from ..models.onboarding_settings import OnboardingSettings  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="NodeConfig")


@attrs.define
class NodeConfig:
    """Base model for Block Config. Actual block configs should subclass from this.

    Attributes:
        annotation_label_spaces (Union[Unset, List['LabelSpaceConfig']]):
        auto_generate_negative_ground_truth_labels (Union[Unset, bool]):  Default: False.
        columns_metadata (Union[Unset, NodeConfigColumnsMetadata]):
        context_datapoint_cls (Union[Unset, str]):
        context_datapoint_cols (Union[Unset, List[str]]):
        data_to_extract (Union[Unset, CandidateIEType]):
        datapoint_cls (Union[Unset, str]):
        datapoint_cols (Union[Unset, List[str]]):
        gt_parent_version_map (Union[Unset, NodeConfigGtParentVersionMap]):
        gt_version_uid (Union[Unset, int]):
        hidden (Union[Unset, bool]):  Default: False.
        label_map (Union[Unset, NodeConfigLabelMap]):
        label_space_config (Union['LabelSpaceConfig', 'NodeConfigLabelSpaceConfigType0', None, Unset]):
        misc_node_info (Union[Unset, NodeConfigMiscNodeInfo]):
        node_name (Union[Unset, str]):
        onboarding_settings (Union[Unset, OnboardingSettings]):
        safe_to_delete (Union[Unset, bool]):  Default: True.
        special_columns (Union[Unset, NodeConfigSpecialColumns]):
    """

    annotation_label_spaces: Union[Unset, List["LabelSpaceConfig"]] = UNSET
    auto_generate_negative_ground_truth_labels: Union[Unset, bool] = False
    columns_metadata: Union[Unset, "NodeConfigColumnsMetadata"] = UNSET
    context_datapoint_cls: Union[Unset, str] = UNSET
    context_datapoint_cols: Union[Unset, List[str]] = UNSET
    data_to_extract: Union[Unset, CandidateIEType] = UNSET
    datapoint_cls: Union[Unset, str] = UNSET
    datapoint_cols: Union[Unset, List[str]] = UNSET
    gt_parent_version_map: Union[Unset, "NodeConfigGtParentVersionMap"] = UNSET
    gt_version_uid: Union[Unset, int] = UNSET
    hidden: Union[Unset, bool] = False
    label_map: Union[Unset, "NodeConfigLabelMap"] = UNSET
    label_space_config: Union[
        "LabelSpaceConfig", "NodeConfigLabelSpaceConfigType0", None, Unset
    ] = UNSET
    misc_node_info: Union[Unset, "NodeConfigMiscNodeInfo"] = UNSET
    node_name: Union[Unset, str] = UNSET
    onboarding_settings: Union[Unset, "OnboardingSettings"] = UNSET
    safe_to_delete: Union[Unset, bool] = True
    special_columns: Union[Unset, "NodeConfigSpecialColumns"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_space_config import LabelSpaceConfig  # noqa: F401
        from ..models.node_config_columns_metadata import (
            NodeConfigColumnsMetadata,  # noqa: F401
        )
        from ..models.node_config_gt_parent_version_map import (
            NodeConfigGtParentVersionMap,  # noqa: F401
        )
        from ..models.node_config_label_map import NodeConfigLabelMap  # noqa: F401
        from ..models.node_config_label_space_config_type_0 import (
            NodeConfigLabelSpaceConfigType0,  # noqa: F401
        )
        from ..models.node_config_misc_node_info import (
            NodeConfigMiscNodeInfo,  # noqa: F401
        )
        from ..models.node_config_special_columns import (
            NodeConfigSpecialColumns,  # noqa: F401
        )
        from ..models.onboarding_settings import OnboardingSettings  # noqa: F401
        # fmt: on
        annotation_label_spaces: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.annotation_label_spaces, Unset):
            annotation_label_spaces = []
            for annotation_label_spaces_item_data in self.annotation_label_spaces:
                annotation_label_spaces_item = (
                    annotation_label_spaces_item_data.to_dict()
                )
                annotation_label_spaces.append(annotation_label_spaces_item)

        auto_generate_negative_ground_truth_labels = (
            self.auto_generate_negative_ground_truth_labels
        )
        columns_metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.columns_metadata, Unset):
            columns_metadata = self.columns_metadata.to_dict()
        context_datapoint_cls = self.context_datapoint_cls
        context_datapoint_cols: Union[Unset, List[str]] = UNSET
        if not isinstance(self.context_datapoint_cols, Unset):
            context_datapoint_cols = self.context_datapoint_cols

        data_to_extract: Union[Unset, str] = UNSET
        if not isinstance(self.data_to_extract, Unset):
            data_to_extract = self.data_to_extract.value

        datapoint_cls = self.datapoint_cls
        datapoint_cols: Union[Unset, List[str]] = UNSET
        if not isinstance(self.datapoint_cols, Unset):
            datapoint_cols = self.datapoint_cols

        gt_parent_version_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.gt_parent_version_map, Unset):
            gt_parent_version_map = self.gt_parent_version_map.to_dict()
        gt_version_uid = self.gt_version_uid
        hidden = self.hidden
        label_map: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_map, Unset):
            label_map = self.label_map.to_dict()
        label_space_config: Union[Dict[str, Any], None, Unset]
        if isinstance(self.label_space_config, Unset):
            label_space_config = UNSET
        elif isinstance(self.label_space_config, NodeConfigLabelSpaceConfigType0):
            label_space_config = self.label_space_config.to_dict()
        elif isinstance(self.label_space_config, LabelSpaceConfig):
            label_space_config = self.label_space_config.to_dict()
        else:
            label_space_config = self.label_space_config
        misc_node_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.misc_node_info, Unset):
            misc_node_info = self.misc_node_info.to_dict()
        node_name = self.node_name
        onboarding_settings: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.onboarding_settings, Unset):
            onboarding_settings = self.onboarding_settings.to_dict()
        safe_to_delete = self.safe_to_delete
        special_columns: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.special_columns, Unset):
            special_columns = self.special_columns.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if annotation_label_spaces is not UNSET:
            field_dict["annotation_label_spaces"] = annotation_label_spaces
        if auto_generate_negative_ground_truth_labels is not UNSET:
            field_dict["auto_generate_negative_ground_truth_labels"] = (
                auto_generate_negative_ground_truth_labels
            )
        if columns_metadata is not UNSET:
            field_dict["columns_metadata"] = columns_metadata
        if context_datapoint_cls is not UNSET:
            field_dict["context_datapoint_cls"] = context_datapoint_cls
        if context_datapoint_cols is not UNSET:
            field_dict["context_datapoint_cols"] = context_datapoint_cols
        if data_to_extract is not UNSET:
            field_dict["data_to_extract"] = data_to_extract
        if datapoint_cls is not UNSET:
            field_dict["datapoint_cls"] = datapoint_cls
        if datapoint_cols is not UNSET:
            field_dict["datapoint_cols"] = datapoint_cols
        if gt_parent_version_map is not UNSET:
            field_dict["gt_parent_version_map"] = gt_parent_version_map
        if gt_version_uid is not UNSET:
            field_dict["gt_version_uid"] = gt_version_uid
        if hidden is not UNSET:
            field_dict["hidden"] = hidden
        if label_map is not UNSET:
            field_dict["label_map"] = label_map
        if label_space_config is not UNSET:
            field_dict["label_space_config"] = label_space_config
        if misc_node_info is not UNSET:
            field_dict["misc_node_info"] = misc_node_info
        if node_name is not UNSET:
            field_dict["node_name"] = node_name
        if onboarding_settings is not UNSET:
            field_dict["onboarding_settings"] = onboarding_settings
        if safe_to_delete is not UNSET:
            field_dict["safe_to_delete"] = safe_to_delete
        if special_columns is not UNSET:
            field_dict["special_columns"] = special_columns

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_space_config import LabelSpaceConfig  # noqa: F401
        from ..models.node_config_columns_metadata import (
            NodeConfigColumnsMetadata,  # noqa: F401
        )
        from ..models.node_config_gt_parent_version_map import (
            NodeConfigGtParentVersionMap,  # noqa: F401
        )
        from ..models.node_config_label_map import NodeConfigLabelMap  # noqa: F401
        from ..models.node_config_label_space_config_type_0 import (
            NodeConfigLabelSpaceConfigType0,  # noqa: F401
        )
        from ..models.node_config_misc_node_info import (
            NodeConfigMiscNodeInfo,  # noqa: F401
        )
        from ..models.node_config_special_columns import (
            NodeConfigSpecialColumns,  # noqa: F401
        )
        from ..models.onboarding_settings import OnboardingSettings  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _annotation_label_spaces = d.pop("annotation_label_spaces", UNSET)
        annotation_label_spaces = []
        _annotation_label_spaces = (
            UNSET if _annotation_label_spaces is None else _annotation_label_spaces
        )
        for annotation_label_spaces_item_data in _annotation_label_spaces or []:
            annotation_label_spaces_item = LabelSpaceConfig.from_dict(
                annotation_label_spaces_item_data
            )

            annotation_label_spaces.append(annotation_label_spaces_item)

        _auto_generate_negative_ground_truth_labels = d.pop(
            "auto_generate_negative_ground_truth_labels", UNSET
        )
        auto_generate_negative_ground_truth_labels = (
            UNSET
            if _auto_generate_negative_ground_truth_labels is None
            else _auto_generate_negative_ground_truth_labels
        )

        _columns_metadata = d.pop("columns_metadata", UNSET)
        _columns_metadata = UNSET if _columns_metadata is None else _columns_metadata
        columns_metadata: Union[Unset, NodeConfigColumnsMetadata]
        if isinstance(_columns_metadata, Unset):
            columns_metadata = UNSET
        else:
            columns_metadata = NodeConfigColumnsMetadata.from_dict(_columns_metadata)

        _context_datapoint_cls = d.pop("context_datapoint_cls", UNSET)
        context_datapoint_cls = (
            UNSET if _context_datapoint_cls is None else _context_datapoint_cls
        )

        _context_datapoint_cols = d.pop("context_datapoint_cols", UNSET)
        context_datapoint_cols = cast(
            List[str],
            UNSET if _context_datapoint_cols is None else _context_datapoint_cols,
        )

        _data_to_extract = d.pop("data_to_extract", UNSET)
        _data_to_extract = UNSET if _data_to_extract is None else _data_to_extract
        data_to_extract: Union[Unset, CandidateIEType]
        if isinstance(_data_to_extract, Unset):
            data_to_extract = UNSET
        else:
            data_to_extract = CandidateIEType(_data_to_extract)

        _datapoint_cls = d.pop("datapoint_cls", UNSET)
        datapoint_cls = UNSET if _datapoint_cls is None else _datapoint_cls

        _datapoint_cols = d.pop("datapoint_cols", UNSET)
        datapoint_cols = cast(
            List[str], UNSET if _datapoint_cols is None else _datapoint_cols
        )

        _gt_parent_version_map = d.pop("gt_parent_version_map", UNSET)
        _gt_parent_version_map = (
            UNSET if _gt_parent_version_map is None else _gt_parent_version_map
        )
        gt_parent_version_map: Union[Unset, NodeConfigGtParentVersionMap]
        if isinstance(_gt_parent_version_map, Unset):
            gt_parent_version_map = UNSET
        else:
            gt_parent_version_map = NodeConfigGtParentVersionMap.from_dict(
                _gt_parent_version_map
            )

        _gt_version_uid = d.pop("gt_version_uid", UNSET)
        gt_version_uid = UNSET if _gt_version_uid is None else _gt_version_uid

        _hidden = d.pop("hidden", UNSET)
        hidden = UNSET if _hidden is None else _hidden

        _label_map = d.pop("label_map", UNSET)
        _label_map = UNSET if _label_map is None else _label_map
        label_map: Union[Unset, NodeConfigLabelMap]
        if isinstance(_label_map, Unset):
            label_map = UNSET
        else:
            label_map = NodeConfigLabelMap.from_dict(_label_map)

        _label_space_config = d.pop("label_space_config", UNSET)

        def _parse_label_space_config(
            data: object,
        ) -> Union["LabelSpaceConfig", "NodeConfigLabelSpaceConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                label_space_config_type_0 = NodeConfigLabelSpaceConfigType0.from_dict(
                    data
                )

                return label_space_config_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                label_space_config_type_1 = LabelSpaceConfig.from_dict(data)

                return label_space_config_type_1
            except:  # noqa: E722
                pass
            return cast(
                Union[
                    "LabelSpaceConfig", "NodeConfigLabelSpaceConfigType0", None, Unset
                ],
                data,
            )

        label_space_config = _parse_label_space_config(
            UNSET if _label_space_config is None else _label_space_config
        )

        _misc_node_info = d.pop("misc_node_info", UNSET)
        _misc_node_info = UNSET if _misc_node_info is None else _misc_node_info
        misc_node_info: Union[Unset, NodeConfigMiscNodeInfo]
        if isinstance(_misc_node_info, Unset):
            misc_node_info = UNSET
        else:
            misc_node_info = NodeConfigMiscNodeInfo.from_dict(_misc_node_info)

        _node_name = d.pop("node_name", UNSET)
        node_name = UNSET if _node_name is None else _node_name

        _onboarding_settings = d.pop("onboarding_settings", UNSET)
        _onboarding_settings = (
            UNSET if _onboarding_settings is None else _onboarding_settings
        )
        onboarding_settings: Union[Unset, OnboardingSettings]
        if isinstance(_onboarding_settings, Unset):
            onboarding_settings = UNSET
        else:
            onboarding_settings = OnboardingSettings.from_dict(_onboarding_settings)

        _safe_to_delete = d.pop("safe_to_delete", UNSET)
        safe_to_delete = UNSET if _safe_to_delete is None else _safe_to_delete

        _special_columns = d.pop("special_columns", UNSET)
        _special_columns = UNSET if _special_columns is None else _special_columns
        special_columns: Union[Unset, NodeConfigSpecialColumns]
        if isinstance(_special_columns, Unset):
            special_columns = UNSET
        else:
            special_columns = NodeConfigSpecialColumns.from_dict(_special_columns)

        obj = cls(
            annotation_label_spaces=annotation_label_spaces,
            auto_generate_negative_ground_truth_labels=auto_generate_negative_ground_truth_labels,
            columns_metadata=columns_metadata,
            context_datapoint_cls=context_datapoint_cls,
            context_datapoint_cols=context_datapoint_cols,
            data_to_extract=data_to_extract,
            datapoint_cls=datapoint_cls,
            datapoint_cols=datapoint_cols,
            gt_parent_version_map=gt_parent_version_map,
            gt_version_uid=gt_version_uid,
            hidden=hidden,
            label_map=label_map,
            label_space_config=label_space_config,
            misc_node_info=misc_node_info,
            node_name=node_name,
            onboarding_settings=onboarding_settings,
            safe_to_delete=safe_to_delete,
            special_columns=special_columns,
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
