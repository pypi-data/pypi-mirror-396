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

from ..models.selection_strategy import SelectionStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_form import AnnotationForm  # noqa: F401
    from ..models.metadata import Metadata  # noqa: F401
    from ..models.trace_index import TraceIndex  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreateDatasetBatchPayload")


@attrs.define
class CreateDatasetBatchPayload:
    """
    Attributes:
        dataset_uid (int):
        annotation_form (Union[Unset, AnnotationForm]):
        assignees (Union[Unset, List[int]]):
        batch_size (Union[Unset, int]):
        datasource_uid (Union[Unset, int]):
        divide_x_uids_evenly_to_assignees (Union[Unset, bool]):  Default: False.
        filter_by_unassigned_x_uids (Union[Unset, bool]):  Default: False.
        label_schema_uids (Union[Unset, List[int]]):
        metadata (Union[Unset, Metadata]):
        name (Union[Unset, str]):
        parent_batch_uid (Union[Unset, int]):
        random_seed (Union[Unset, int]):  Default: 123.
        randomize (Union[Unset, bool]):  Default: False.
        selection_strategy (Union[Unset, SelectionStrategy]):
        split (Union[Unset, str]):
        trace_indices (Union[Unset, List['TraceIndex']]):
        x_uids (Union[Unset, List[str]]):
    """

    dataset_uid: int
    annotation_form: Union[Unset, "AnnotationForm"] = UNSET
    assignees: Union[Unset, List[int]] = UNSET
    batch_size: Union[Unset, int] = UNSET
    datasource_uid: Union[Unset, int] = UNSET
    divide_x_uids_evenly_to_assignees: Union[Unset, bool] = False
    filter_by_unassigned_x_uids: Union[Unset, bool] = False
    label_schema_uids: Union[Unset, List[int]] = UNSET
    metadata: Union[Unset, "Metadata"] = UNSET
    name: Union[Unset, str] = UNSET
    parent_batch_uid: Union[Unset, int] = UNSET
    random_seed: Union[Unset, int] = 123
    randomize: Union[Unset, bool] = False
    selection_strategy: Union[Unset, SelectionStrategy] = UNSET
    split: Union[Unset, str] = UNSET
    trace_indices: Union[Unset, List["TraceIndex"]] = UNSET
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.metadata import Metadata  # noqa: F401
        from ..models.trace_index import TraceIndex  # noqa: F401
        # fmt: on
        dataset_uid = self.dataset_uid
        annotation_form: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotation_form, Unset):
            annotation_form = self.annotation_form.to_dict()
        assignees: Union[Unset, List[int]] = UNSET
        if not isinstance(self.assignees, Unset):
            assignees = self.assignees

        batch_size = self.batch_size
        datasource_uid = self.datasource_uid
        divide_x_uids_evenly_to_assignees = self.divide_x_uids_evenly_to_assignees
        filter_by_unassigned_x_uids = self.filter_by_unassigned_x_uids
        label_schema_uids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.label_schema_uids, Unset):
            label_schema_uids = self.label_schema_uids

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        name = self.name
        parent_batch_uid = self.parent_batch_uid
        random_seed = self.random_seed
        randomize = self.randomize
        selection_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.selection_strategy, Unset):
            selection_strategy = self.selection_strategy.value

        split = self.split
        trace_indices: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.trace_indices, Unset):
            trace_indices = []
            for trace_indices_item_data in self.trace_indices:
                trace_indices_item = trace_indices_item_data.to_dict()
                trace_indices.append(trace_indices_item)

        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_uid": dataset_uid,
            }
        )
        if annotation_form is not UNSET:
            field_dict["annotation_form"] = annotation_form
        if assignees is not UNSET:
            field_dict["assignees"] = assignees
        if batch_size is not UNSET:
            field_dict["batch_size"] = batch_size
        if datasource_uid is not UNSET:
            field_dict["datasource_uid"] = datasource_uid
        if divide_x_uids_evenly_to_assignees is not UNSET:
            field_dict["divide_x_uids_evenly_to_assignees"] = (
                divide_x_uids_evenly_to_assignees
            )
        if filter_by_unassigned_x_uids is not UNSET:
            field_dict["filter_by_unassigned_x_uids"] = filter_by_unassigned_x_uids
        if label_schema_uids is not UNSET:
            field_dict["label_schema_uids"] = label_schema_uids
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if name is not UNSET:
            field_dict["name"] = name
        if parent_batch_uid is not UNSET:
            field_dict["parent_batch_uid"] = parent_batch_uid
        if random_seed is not UNSET:
            field_dict["random_seed"] = random_seed
        if randomize is not UNSET:
            field_dict["randomize"] = randomize
        if selection_strategy is not UNSET:
            field_dict["selection_strategy"] = selection_strategy
        if split is not UNSET:
            field_dict["split"] = split
        if trace_indices is not UNSET:
            field_dict["trace_indices"] = trace_indices
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.metadata import Metadata  # noqa: F401
        from ..models.trace_index import TraceIndex  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        dataset_uid = d.pop("dataset_uid")

        _annotation_form = d.pop("annotation_form", UNSET)
        _annotation_form = UNSET if _annotation_form is None else _annotation_form
        annotation_form: Union[Unset, AnnotationForm]
        if isinstance(_annotation_form, Unset):
            annotation_form = UNSET
        else:
            annotation_form = AnnotationForm.from_dict(_annotation_form)

        _assignees = d.pop("assignees", UNSET)
        assignees = cast(List[int], UNSET if _assignees is None else _assignees)

        _batch_size = d.pop("batch_size", UNSET)
        batch_size = UNSET if _batch_size is None else _batch_size

        _datasource_uid = d.pop("datasource_uid", UNSET)
        datasource_uid = UNSET if _datasource_uid is None else _datasource_uid

        _divide_x_uids_evenly_to_assignees = d.pop(
            "divide_x_uids_evenly_to_assignees", UNSET
        )
        divide_x_uids_evenly_to_assignees = (
            UNSET
            if _divide_x_uids_evenly_to_assignees is None
            else _divide_x_uids_evenly_to_assignees
        )

        _filter_by_unassigned_x_uids = d.pop("filter_by_unassigned_x_uids", UNSET)
        filter_by_unassigned_x_uids = (
            UNSET
            if _filter_by_unassigned_x_uids is None
            else _filter_by_unassigned_x_uids
        )

        _label_schema_uids = d.pop("label_schema_uids", UNSET)
        label_schema_uids = cast(
            List[int], UNSET if _label_schema_uids is None else _label_schema_uids
        )

        _metadata = d.pop("metadata", UNSET)
        _metadata = UNSET if _metadata is None else _metadata
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        _name = d.pop("name", UNSET)
        name = UNSET if _name is None else _name

        _parent_batch_uid = d.pop("parent_batch_uid", UNSET)
        parent_batch_uid = UNSET if _parent_batch_uid is None else _parent_batch_uid

        _random_seed = d.pop("random_seed", UNSET)
        random_seed = UNSET if _random_seed is None else _random_seed

        _randomize = d.pop("randomize", UNSET)
        randomize = UNSET if _randomize is None else _randomize

        _selection_strategy = d.pop("selection_strategy", UNSET)
        _selection_strategy = (
            UNSET if _selection_strategy is None else _selection_strategy
        )
        selection_strategy: Union[Unset, SelectionStrategy]
        if isinstance(_selection_strategy, Unset):
            selection_strategy = UNSET
        else:
            selection_strategy = SelectionStrategy(_selection_strategy)

        _split = d.pop("split", UNSET)
        split = UNSET if _split is None else _split

        _trace_indices = d.pop("trace_indices", UNSET)
        trace_indices = []
        _trace_indices = UNSET if _trace_indices is None else _trace_indices
        for trace_indices_item_data in _trace_indices or []:
            trace_indices_item = TraceIndex.from_dict(trace_indices_item_data)

            trace_indices.append(trace_indices_item)

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            dataset_uid=dataset_uid,
            annotation_form=annotation_form,
            assignees=assignees,
            batch_size=batch_size,
            datasource_uid=datasource_uid,
            divide_x_uids_evenly_to_assignees=divide_x_uids_evenly_to_assignees,
            filter_by_unassigned_x_uids=filter_by_unassigned_x_uids,
            label_schema_uids=label_schema_uids,
            metadata=metadata,
            name=name,
            parent_batch_uid=parent_batch_uid,
            random_seed=random_seed,
            randomize=randomize,
            selection_strategy=selection_strategy,
            split=split,
            trace_indices=trace_indices,
            x_uids=x_uids,
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
