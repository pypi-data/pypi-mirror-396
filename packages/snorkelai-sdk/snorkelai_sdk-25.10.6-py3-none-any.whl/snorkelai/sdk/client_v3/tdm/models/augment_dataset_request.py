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
    from ..models.augment_dataset_request_cacher_kwargs import (
        AugmentDatasetRequestCacherKwargs,  # noqa: F401
    )
    from ..models.augment_dataset_request_fm_hyperparameters import (
        AugmentDatasetRequestFmHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="AugmentDatasetRequest")


@attrs.define
class AugmentDatasetRequest:
    """
    Attributes:
        model_name (str):
        prompt (str):
        workspace_uid (int):
        x_uids (List[str]):
        cacher_kwargs (Union[Unset, AugmentDatasetRequestCacherKwargs]):
        fields (Union[Unset, List[str]]):
        fm_hyperparameters (Union[Unset, AugmentDatasetRequestFmHyperparameters]):
        num_runs (Union[Unset, int]):  Default: 1.
        skip_errors (Union[Unset, bool]):  Default: True.
        use_cached_results (Union[Unset, bool]):  Default: False.
    """

    model_name: str
    prompt: str
    workspace_uid: int
    x_uids: List[str]
    cacher_kwargs: Union[Unset, "AugmentDatasetRequestCacherKwargs"] = UNSET
    fields: Union[Unset, List[str]] = UNSET
    fm_hyperparameters: Union[Unset, "AugmentDatasetRequestFmHyperparameters"] = UNSET
    num_runs: Union[Unset, int] = 1
    skip_errors: Union[Unset, bool] = True
    use_cached_results: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.augment_dataset_request_cacher_kwargs import (
            AugmentDatasetRequestCacherKwargs,  # noqa: F401
        )
        from ..models.augment_dataset_request_fm_hyperparameters import (
            AugmentDatasetRequestFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        model_name = self.model_name
        prompt = self.prompt
        workspace_uid = self.workspace_uid
        x_uids = self.x_uids

        cacher_kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cacher_kwargs, Unset):
            cacher_kwargs = self.cacher_kwargs.to_dict()
        fields: Union[Unset, List[str]] = UNSET
        if not isinstance(self.fields, Unset):
            fields = self.fields

        fm_hyperparameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fm_hyperparameters, Unset):
            fm_hyperparameters = self.fm_hyperparameters.to_dict()
        num_runs = self.num_runs
        skip_errors = self.skip_errors
        use_cached_results = self.use_cached_results

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_name": model_name,
                "prompt": prompt,
                "workspace_uid": workspace_uid,
                "x_uids": x_uids,
            }
        )
        if cacher_kwargs is not UNSET:
            field_dict["cacher_kwargs"] = cacher_kwargs
        if fields is not UNSET:
            field_dict["fields"] = fields
        if fm_hyperparameters is not UNSET:
            field_dict["fm_hyperparameters"] = fm_hyperparameters
        if num_runs is not UNSET:
            field_dict["num_runs"] = num_runs
        if skip_errors is not UNSET:
            field_dict["skip_errors"] = skip_errors
        if use_cached_results is not UNSET:
            field_dict["use_cached_results"] = use_cached_results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.augment_dataset_request_cacher_kwargs import (
            AugmentDatasetRequestCacherKwargs,  # noqa: F401
        )
        from ..models.augment_dataset_request_fm_hyperparameters import (
            AugmentDatasetRequestFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        model_name = d.pop("model_name")

        prompt = d.pop("prompt")

        workspace_uid = d.pop("workspace_uid")

        x_uids = cast(List[str], d.pop("x_uids"))

        _cacher_kwargs = d.pop("cacher_kwargs", UNSET)
        _cacher_kwargs = UNSET if _cacher_kwargs is None else _cacher_kwargs
        cacher_kwargs: Union[Unset, AugmentDatasetRequestCacherKwargs]
        if isinstance(_cacher_kwargs, Unset):
            cacher_kwargs = UNSET
        else:
            cacher_kwargs = AugmentDatasetRequestCacherKwargs.from_dict(_cacher_kwargs)

        _fields = d.pop("fields", UNSET)
        fields = cast(List[str], UNSET if _fields is None else _fields)

        _fm_hyperparameters = d.pop("fm_hyperparameters", UNSET)
        _fm_hyperparameters = (
            UNSET if _fm_hyperparameters is None else _fm_hyperparameters
        )
        fm_hyperparameters: Union[Unset, AugmentDatasetRequestFmHyperparameters]
        if isinstance(_fm_hyperparameters, Unset):
            fm_hyperparameters = UNSET
        else:
            fm_hyperparameters = AugmentDatasetRequestFmHyperparameters.from_dict(
                _fm_hyperparameters
            )

        _num_runs = d.pop("num_runs", UNSET)
        num_runs = UNSET if _num_runs is None else _num_runs

        _skip_errors = d.pop("skip_errors", UNSET)
        skip_errors = UNSET if _skip_errors is None else _skip_errors

        _use_cached_results = d.pop("use_cached_results", UNSET)
        use_cached_results = (
            UNSET if _use_cached_results is None else _use_cached_results
        )

        obj = cls(
            model_name=model_name,
            prompt=prompt,
            workspace_uid=workspace_uid,
            x_uids=x_uids,
            cacher_kwargs=cacher_kwargs,
            fields=fields,
            fm_hyperparameters=fm_hyperparameters,
            num_runs=num_runs,
            skip_errors=skip_errors,
            use_cached_results=use_cached_results,
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
