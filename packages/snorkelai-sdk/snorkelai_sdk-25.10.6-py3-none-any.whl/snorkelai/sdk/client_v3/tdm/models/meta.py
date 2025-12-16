import datetime
from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Union,
)

import attrs
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Meta")


@attrs.define
class Meta:
    """All "meta" sub-attributes are assigned by the service provider (have a "mutability" of "readOnly"), and all of these
    sub-attributes have a "returned" characteristic of "default".

    This attribute SHALL be ignored when provided by clients.  "meta" contains the following sub-attributes:

        Attributes:
            created (Union[Unset, datetime.datetime]): The "DateTime" that the resource was added to the service provider.

                This attribute MUST be a DateTime.
            lastmodified (Union[Unset, datetime.datetime]): The most recent DateTime that the details of this resource were
                updated
                at the service provider.

                If this resource has never been modified since its initial creation,
                the value MUST be the same as the value of "created".
            location (Union[Unset, str]): The URI of the resource being returned.

                This value MUST be the same as the "Content-Location" HTTP response
                header (see Section 3.1.4.2 of [RFC7231]).
            resourcetype (Union[Unset, str]): The name of the resource type of the resource.

                This attribute has a mutability of "readOnly" and "caseExact" as
                "true".
            version (Union[Unset, str]): The version of the resource being returned.

                This value must be the same as the entity-tag (ETag) HTTP response
                header (see Sections 2.1 and 2.3 of [RFC7232]).  This attribute has
                "caseExact" as "true".  Service provider support for this attribute
                is optional and subject to the service provider's support for
                versioning (see Section 3.14 of [RFC7644]).  If a service provider
                provides "version" (entity-tag) for a representation and the
                generation of that entity-tag does not satisfy all of the
                characteristics of a strong validator (see Section 2.1 of
                [RFC7232]), then the origin server MUST mark the "version" (entity-
                tag) as weak by prefixing its opaque value with "W/" (case
                sensitive).
    """

    created: Union[Unset, datetime.datetime] = UNSET
    lastmodified: Union[Unset, datetime.datetime] = UNSET
    location: Union[Unset, str] = UNSET
    resourcetype: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()
        lastmodified: Union[Unset, str] = UNSET
        if not isinstance(self.lastmodified, Unset):
            lastmodified = self.lastmodified.isoformat()
        location = self.location
        resourcetype = self.resourcetype
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if created is not UNSET:
            field_dict["created"] = created
        if lastmodified is not UNSET:
            field_dict["lastmodified"] = lastmodified
        if location is not UNSET:
            field_dict["location"] = location
        if resourcetype is not UNSET:
            field_dict["resourcetype"] = resourcetype
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _created = d.pop("created", UNSET)
        _created = UNSET if _created is None else _created
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        _lastmodified = d.pop("lastmodified", UNSET)
        _lastmodified = UNSET if _lastmodified is None else _lastmodified
        lastmodified: Union[Unset, datetime.datetime]
        if isinstance(_lastmodified, Unset):
            lastmodified = UNSET
        else:
            lastmodified = isoparse(_lastmodified)

        _location = d.pop("location", UNSET)
        location = UNSET if _location is None else _location

        _resourcetype = d.pop("resourcetype", UNSET)
        resourcetype = UNSET if _resourcetype is None else _resourcetype

        _version = d.pop("version", UNSET)
        version = UNSET if _version is None else _version

        obj = cls(
            created=created,
            lastmodified=lastmodified,
            location=location,
            resourcetype=resourcetype,
            version=version,
        )
        return obj
