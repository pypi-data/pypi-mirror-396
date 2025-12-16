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
    from ..models.list_secret_params_kwargs import ListSecretParamsKwargs  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ListSecretParams")


@attrs.define
class ListSecretParams:
    """
    Attributes:
        kwargs (Union[Unset, ListSecretParamsKwargs]):
        secret_store (Union[Unset, str]):  Default: 'local_store'.
        workspace_uid (Union[Unset, int]):  Default: 1.
    """

    kwargs: Union[Unset, "ListSecretParamsKwargs"] = UNSET
    secret_store: Union[Unset, str] = "local_store"
    workspace_uid: Union[Unset, int] = 1
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.list_secret_params_kwargs import (
            ListSecretParamsKwargs,  # noqa: F401
        )
        # fmt: on
        kwargs: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.kwargs, Unset):
            kwargs = self.kwargs.to_dict()
        secret_store = self.secret_store
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if kwargs is not UNSET:
            field_dict["kwargs"] = kwargs
        if secret_store is not UNSET:
            field_dict["secret_store"] = secret_store
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.list_secret_params_kwargs import (
            ListSecretParamsKwargs,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        _kwargs = d.pop("kwargs", UNSET)
        _kwargs = UNSET if _kwargs is None else _kwargs
        kwargs: Union[Unset, ListSecretParamsKwargs]
        if isinstance(_kwargs, Unset):
            kwargs = UNSET
        else:
            kwargs = ListSecretParamsKwargs.from_dict(_kwargs)

        _secret_store = d.pop("secret_store", UNSET)
        secret_store = UNSET if _secret_store is None else _secret_store

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            kwargs=kwargs,
            secret_store=secret_store,
            workspace_uid=workspace_uid,
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
