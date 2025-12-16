import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class SCIMSchemaUrn(StrEnum):
    URNIETFPARAMSSCIMSCHEMASCORE2_0GROUP = "urn:ietf:params:scim:schemas:core:2.0:Group"
    URNIETFPARAMSSCIMSCHEMASCORE2_0USER = "urn:ietf:params:scim:schemas:core:2.0:User"
    URNIETFPARAMSSCIMSCHEMASEXTENSIONENTERPRISE2_0USER = (
        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    )
