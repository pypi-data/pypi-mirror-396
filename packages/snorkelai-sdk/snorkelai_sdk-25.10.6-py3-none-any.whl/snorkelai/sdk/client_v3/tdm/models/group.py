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
    from ..models.group_member import GroupMember  # noqa: F401
    from ..models.meta import Meta  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="Group")


@attrs.define
class Group:
    """
    Attributes:
        displayname (Union[Unset, str]): A human-readable name for the Group.
        externalid (Union[Unset, str]): A String that is an identifier for the resource as defined by the
            provisioning client.
        id (Union[Unset, str]): A unique identifier for a SCIM resource as defined by the service
            provider.

            id is mandatory is the resource representation, but is forbidden in
            resource creation or replacement requests.
        members (Union[Unset, List['GroupMember']]): A list of members of the Group.
        meta (Union[Unset, Meta]): All "meta" sub-attributes are assigned by the service provider (have a "mutability"
            of "readOnly"), and all of these sub-attributes have a "returned" characteristic of "default".

            This attribute SHALL be ignored when provided by clients.  "meta" contains the following sub-attributes:
        schemas (Union[Unset, List[str]]):
    """

    displayname: Union[Unset, str] = UNSET
    externalid: Union[Unset, str] = UNSET
    id: Union[Unset, str] = UNSET
    members: Union[Unset, List["GroupMember"]] = UNSET
    meta: Union[Unset, "Meta"] = UNSET
    schemas: Union[Unset, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.group_member import GroupMember  # noqa: F401
        from ..models.meta import Meta  # noqa: F401
        # fmt: on
        displayname = self.displayname
        externalid = self.externalid
        id = self.id
        members: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)

        meta: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.meta, Unset):
            meta = self.meta.to_dict()
        schemas: Union[Unset, List[str]] = UNSET
        if not isinstance(self.schemas, Unset):
            schemas = self.schemas

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if displayname is not UNSET:
            field_dict["displayname"] = displayname
        if externalid is not UNSET:
            field_dict["externalid"] = externalid
        if id is not UNSET:
            field_dict["id"] = id
        if members is not UNSET:
            field_dict["members"] = members
        if meta is not UNSET:
            field_dict["meta"] = meta
        if schemas is not UNSET:
            field_dict["schemas"] = schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.group_member import GroupMember  # noqa: F401
        from ..models.meta import Meta  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        _displayname = d.pop("displayname", UNSET)
        displayname = UNSET if _displayname is None else _displayname

        _externalid = d.pop("externalid", UNSET)
        externalid = UNSET if _externalid is None else _externalid

        _id = d.pop("id", UNSET)
        id = UNSET if _id is None else _id

        _members = d.pop("members", UNSET)
        members = []
        _members = UNSET if _members is None else _members
        for members_item_data in _members or []:
            members_item = GroupMember.from_dict(members_item_data)

            members.append(members_item)

        _meta = d.pop("meta", UNSET)
        _meta = UNSET if _meta is None else _meta
        meta: Union[Unset, Meta]
        if isinstance(_meta, Unset):
            meta = UNSET
        else:
            meta = Meta.from_dict(_meta)

        _schemas = d.pop("schemas", UNSET)
        schemas = cast(List[str], UNSET if _schemas is None else _schemas)

        obj = cls(
            displayname=displayname,
            externalid=externalid,
            id=id,
            members=members,
            meta=meta,
            schemas=schemas,
        )
        return obj
