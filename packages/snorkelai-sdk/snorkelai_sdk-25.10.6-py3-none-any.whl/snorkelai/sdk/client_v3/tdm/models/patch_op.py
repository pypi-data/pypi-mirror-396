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
    from ..models.patch_operation import PatchOperation  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="PatchOp")


@attrs.define
class PatchOp:
    """Patch Operation as defined in :rfc:`RFC7644 §3.5.2 <7644#section-3.5.2>`.

    .. todo::

        The models for Patch operations are defined, but their behavior is not implemented nor tested yet.

        Attributes:
            operations (Union[Unset, List['PatchOperation']]): The body of an HTTP PATCH request MUST contain the attribute
                "Operations", whose value is an array of one or more PATCH operations.
            schemas (Union[Unset, List[str]]):
    """

    operations: Union[Unset, List["PatchOperation"]] = UNSET
    schemas: Union[Unset, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.patch_operation import PatchOperation  # noqa: F401
        # fmt: on
        operations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.operations, Unset):
            operations = []
            for operations_item_data in self.operations:
                operations_item = operations_item_data.to_dict()
                operations.append(operations_item)

        schemas: Union[Unset, List[str]] = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if operations is not UNSET:
            field_dict["operations"] = operations
        if schemas is not UNSET:
            field_dict["schemas"] = schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.patch_operation import PatchOperation  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _operations = d.pop("operations", UNSET)
        operations = []
        _operations = UNSET if _operations is None else _operations
        for operations_item_data in _operations or []:
            operations_item = PatchOperation.from_dict(operations_item_data)

            operations.append(operations_item)

        _schemas = d.pop("schemas", UNSET)
        schemas = cast(List[str], UNSET if _schemas is None else _schemas)

        obj = cls(
            operations=operations,
            schemas=schemas,
        )
        return obj
