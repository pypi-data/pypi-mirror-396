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
    from ..models.group import Group  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ListResponseGroup")


@attrs.define
class ListResponseGroup:
    """
    Attributes:
        itemsperpage (Union[Unset, int]): The number of resources returned in a list response page.
        resources (Union[Unset, List['Group']]): A multi-valued list of complex objects containing the requested
            resources.
        schemas (Union[Unset, List[str]]):
        startindex (Union[Unset, int]): The 1-based index of the first result in the current set of list
            results.
        totalresults (Union[Unset, int]): The total number of results returned by the list or query operation.
    """

    itemsperpage: Union[Unset, int] = UNSET
    resources: Union[Unset, List["Group"]] = UNSET
    schemas: Union[Unset, List[str]] = UNSET
    startindex: Union[Unset, int] = UNSET
    totalresults: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.group import Group  # noqa: F401
        # fmt: on
        itemsperpage = self.itemsperpage
        resources: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item = resources_item_data.to_dict()
                resources.append(resources_item)

        schemas: Union[Unset, List[str]] = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        startindex = self.startindex
        totalresults = self.totalresults

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if itemsperpage is not UNSET:
            field_dict["itemsperpage"] = itemsperpage
        if resources is not UNSET:
            field_dict["resources"] = resources
        if schemas is not UNSET:
            field_dict["schemas"] = schemas
        if startindex is not UNSET:
            field_dict["startindex"] = startindex
        if totalresults is not UNSET:
            field_dict["totalresults"] = totalresults

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.group import Group  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _itemsperpage = d.pop("itemsperpage", UNSET)
        itemsperpage = UNSET if _itemsperpage is None else _itemsperpage

        _resources = d.pop("resources", UNSET)
        resources = []
        _resources = UNSET if _resources is None else _resources
        for resources_item_data in _resources or []:
            resources_item = Group.from_dict(resources_item_data)

            resources.append(resources_item)

        _schemas = d.pop("schemas", UNSET)
        schemas = cast(List[str], UNSET if _schemas is None else _schemas)

        _startindex = d.pop("startindex", UNSET)
        startindex = UNSET if _startindex is None else _startindex

        _totalresults = d.pop("totalresults", UNSET)
        totalresults = UNSET if _totalresults is None else _totalresults

        obj = cls(
            itemsperpage=itemsperpage,
            resources=resources,
            schemas=schemas,
            startindex=startindex,
            totalresults=totalresults,
        )
        return obj
