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

from ..models.llm_type import LLMType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.prompt_fm_dataset_request_cacher_kwargs import (
        PromptFMDatasetRequestCacherKwargs,  # noqa: F401
    )
    from ..models.prompt_fm_dataset_request_fm_hyperparameters import (
        PromptFMDatasetRequestFmHyperparameters,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptFMDatasetRequest")


@attrs.define
class PromptFMDatasetRequest:
    """
    Attributes:
        model_name (str):
        prompt (str):
        workspace_uid (int):
        cacher_kwargs (Union[Unset, PromptFMDatasetRequestCacherKwargs]):
        fm_hyperparameters (Union[Unset, PromptFMDatasetRequestFmHyperparameters]):
        model_type (Union[Unset, LLMType]):
        num_runs (Union[Unset, int]):  Default: 1.
        prompt_init_param (Union[Unset, str]):
        skip_errors (Union[Unset, bool]):  Default: True.
        system_prompt (Union[Unset, str]):
        use_cached_results (Union[Unset, bool]):  Default: False.
        x_uids (Union[Unset, List[str]]):
    """

    model_name: str
    prompt: str
    workspace_uid: int
    cacher_kwargs: Union[Unset, "PromptFMDatasetRequestCacherKwargs"] = UNSET
    fm_hyperparameters: Union[Unset, "PromptFMDatasetRequestFmHyperparameters"] = UNSET
    model_type: Union[Unset, LLMType] = UNSET
    num_runs: Union[Unset, int] = 1
    prompt_init_param: Union[Unset, str] = UNSET
    skip_errors: Union[Unset, bool] = True
    system_prompt: Union[Unset, str] = UNSET
    use_cached_results: Union[Unset, bool] = False
    x_uids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_fm_dataset_request_cacher_kwargs import (
            PromptFMDatasetRequestCacherKwargs,  # noqa: F401
        )
        from ..models.prompt_fm_dataset_request_fm_hyperparameters import (
            PromptFMDatasetRequestFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        model_name = self.model_name
        prompt = self.prompt
        workspace_uid = self.workspace_uid
        cacher_kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cacher_kwargs, Unset):
            cacher_kwargs = self.cacher_kwargs.to_dict()
        fm_hyperparameters: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fm_hyperparameters, Unset):
            fm_hyperparameters = self.fm_hyperparameters.to_dict()
        model_type: Union[Unset, str] = UNSET
        if not isinstance(self.model_type, Unset):
            model_type = self.model_type.value

        num_runs = self.num_runs
        prompt_init_param = self.prompt_init_param
        skip_errors = self.skip_errors
        system_prompt = self.system_prompt
        use_cached_results = self.use_cached_results
        x_uids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.x_uids, Unset):
            x_uids = self.x_uids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_name": model_name,
                "prompt": prompt,
                "workspace_uid": workspace_uid,
            }
        )
        if cacher_kwargs is not UNSET:
            field_dict["cacher_kwargs"] = cacher_kwargs
        if fm_hyperparameters is not UNSET:
            field_dict["fm_hyperparameters"] = fm_hyperparameters
        if model_type is not UNSET:
            field_dict["model_type"] = model_type
        if num_runs is not UNSET:
            field_dict["num_runs"] = num_runs
        if prompt_init_param is not UNSET:
            field_dict["prompt_init_param"] = prompt_init_param
        if skip_errors is not UNSET:
            field_dict["skip_errors"] = skip_errors
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if use_cached_results is not UNSET:
            field_dict["use_cached_results"] = use_cached_results
        if x_uids is not UNSET:
            field_dict["x_uids"] = x_uids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_fm_dataset_request_cacher_kwargs import (
            PromptFMDatasetRequestCacherKwargs,  # noqa: F401
        )
        from ..models.prompt_fm_dataset_request_fm_hyperparameters import (
            PromptFMDatasetRequestFmHyperparameters,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        model_name = d.pop("model_name")

        prompt = d.pop("prompt")

        workspace_uid = d.pop("workspace_uid")

        _cacher_kwargs = d.pop("cacher_kwargs", UNSET)
        _cacher_kwargs = UNSET if _cacher_kwargs is None else _cacher_kwargs
        cacher_kwargs: Union[Unset, PromptFMDatasetRequestCacherKwargs]
        if isinstance(_cacher_kwargs, Unset):
            cacher_kwargs = UNSET
        else:
            cacher_kwargs = PromptFMDatasetRequestCacherKwargs.from_dict(_cacher_kwargs)

        _fm_hyperparameters = d.pop("fm_hyperparameters", UNSET)
        _fm_hyperparameters = (
            UNSET if _fm_hyperparameters is None else _fm_hyperparameters
        )
        fm_hyperparameters: Union[Unset, PromptFMDatasetRequestFmHyperparameters]
        if isinstance(_fm_hyperparameters, Unset):
            fm_hyperparameters = UNSET
        else:
            fm_hyperparameters = PromptFMDatasetRequestFmHyperparameters.from_dict(
                _fm_hyperparameters
            )

        _model_type = d.pop("model_type", UNSET)
        _model_type = UNSET if _model_type is None else _model_type
        model_type: Union[Unset, LLMType]
        if isinstance(_model_type, Unset):
            model_type = UNSET
        else:
            model_type = LLMType(_model_type)

        _num_runs = d.pop("num_runs", UNSET)
        num_runs = UNSET if _num_runs is None else _num_runs

        _prompt_init_param = d.pop("prompt_init_param", UNSET)
        prompt_init_param = UNSET if _prompt_init_param is None else _prompt_init_param

        _skip_errors = d.pop("skip_errors", UNSET)
        skip_errors = UNSET if _skip_errors is None else _skip_errors

        _system_prompt = d.pop("system_prompt", UNSET)
        system_prompt = UNSET if _system_prompt is None else _system_prompt

        _use_cached_results = d.pop("use_cached_results", UNSET)
        use_cached_results = (
            UNSET if _use_cached_results is None else _use_cached_results
        )

        _x_uids = d.pop("x_uids", UNSET)
        x_uids = cast(List[str], UNSET if _x_uids is None else _x_uids)

        obj = cls(
            model_name=model_name,
            prompt=prompt,
            workspace_uid=workspace_uid,
            cacher_kwargs=cacher_kwargs,
            fm_hyperparameters=fm_hyperparameters,
            model_type=model_type,
            num_runs=num_runs,
            prompt_init_param=prompt_init_param,
            skip_errors=skip_errors,
            system_prompt=system_prompt,
            use_cached_results=use_cached_results,
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
