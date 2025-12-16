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
    from ..models.prompt_fm_request_cacher_kwargs import (
        PromptFMRequestCacherKwargs,  # noqa: F401
    )
    from ..models.prompt_fm_request_fm_hyperparameters import (
        PromptFMRequestFmHyperparameters,  # noqa: F401
    )
    from ..models.prompt_fm_request_input_data_item_type_1 import (
        PromptFMRequestInputDataItemType1,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="PromptFMRequest")


@attrs.define
class PromptFMRequest:
    """
    Attributes:
        input_data (List[Union['PromptFMRequestInputDataItemType1', str]]):
        model_name (str):
        workspace_uid (int):
        cacher_kwargs (Union[Unset, PromptFMRequestCacherKwargs]):
        fm_hyperparameters (Union[Unset, PromptFMRequestFmHyperparameters]):
        model_type (Union[Unset, LLMType]):
        num_runs (Union[Unset, int]):  Default: 1.
        prompt_init_param (Union[Unset, str]):
        skip_errors (Union[Unset, bool]):  Default: True.
        use_cached_results (Union[Unset, bool]):  Default: False.
    """

    input_data: List[Union["PromptFMRequestInputDataItemType1", str]]
    model_name: str
    workspace_uid: int
    cacher_kwargs: Union[Unset, "PromptFMRequestCacherKwargs"] = UNSET
    fm_hyperparameters: Union[Unset, "PromptFMRequestFmHyperparameters"] = UNSET
    model_type: Union[Unset, LLMType] = UNSET
    num_runs: Union[Unset, int] = 1
    prompt_init_param: Union[Unset, str] = UNSET
    skip_errors: Union[Unset, bool] = True
    use_cached_results: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.prompt_fm_request_cacher_kwargs import (
            PromptFMRequestCacherKwargs,  # noqa: F401
        )
        from ..models.prompt_fm_request_fm_hyperparameters import (
            PromptFMRequestFmHyperparameters,  # noqa: F401
        )
        from ..models.prompt_fm_request_input_data_item_type_1 import (
            PromptFMRequestInputDataItemType1,  # noqa: F401
        )
        # fmt: on
        input_data = []
        for input_data_item_data in self.input_data:
            input_data_item: Union[Dict[str, Any], str]
            if isinstance(input_data_item_data, PromptFMRequestInputDataItemType1):
                input_data_item = input_data_item_data.to_dict()
            else:
                input_data_item = input_data_item_data
            input_data.append(input_data_item)

        model_name = self.model_name
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
        use_cached_results = self.use_cached_results

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_data": input_data,
                "model_name": model_name,
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
        if use_cached_results is not UNSET:
            field_dict["use_cached_results"] = use_cached_results

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.prompt_fm_request_cacher_kwargs import (
            PromptFMRequestCacherKwargs,  # noqa: F401
        )
        from ..models.prompt_fm_request_fm_hyperparameters import (
            PromptFMRequestFmHyperparameters,  # noqa: F401
        )
        from ..models.prompt_fm_request_input_data_item_type_1 import (
            PromptFMRequestInputDataItemType1,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        input_data = []
        _input_data = d.pop("input_data")
        for input_data_item_data in _input_data:

            def _parse_input_data_item(
                data: object,
            ) -> Union["PromptFMRequestInputDataItemType1", str]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    input_data_item_type_1 = (
                        PromptFMRequestInputDataItemType1.from_dict(data)
                    )

                    return input_data_item_type_1
                except:  # noqa: E722
                    pass
                return cast(Union["PromptFMRequestInputDataItemType1", str], data)

            input_data_item = _parse_input_data_item(input_data_item_data)

            input_data.append(input_data_item)

        model_name = d.pop("model_name")

        workspace_uid = d.pop("workspace_uid")

        _cacher_kwargs = d.pop("cacher_kwargs", UNSET)
        _cacher_kwargs = UNSET if _cacher_kwargs is None else _cacher_kwargs
        cacher_kwargs: Union[Unset, PromptFMRequestCacherKwargs]
        if isinstance(_cacher_kwargs, Unset):
            cacher_kwargs = UNSET
        else:
            cacher_kwargs = PromptFMRequestCacherKwargs.from_dict(_cacher_kwargs)

        _fm_hyperparameters = d.pop("fm_hyperparameters", UNSET)
        _fm_hyperparameters = (
            UNSET if _fm_hyperparameters is None else _fm_hyperparameters
        )
        fm_hyperparameters: Union[Unset, PromptFMRequestFmHyperparameters]
        if isinstance(_fm_hyperparameters, Unset):
            fm_hyperparameters = UNSET
        else:
            fm_hyperparameters = PromptFMRequestFmHyperparameters.from_dict(
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

        _use_cached_results = d.pop("use_cached_results", UNSET)
        use_cached_results = (
            UNSET if _use_cached_results is None else _use_cached_results
        )

        obj = cls(
            input_data=input_data,
            model_name=model_name,
            workspace_uid=workspace_uid,
            cacher_kwargs=cacher_kwargs,
            fm_hyperparameters=fm_hyperparameters,
            model_type=model_type,
            num_runs=num_runs,
            prompt_init_param=prompt_init_param,
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
