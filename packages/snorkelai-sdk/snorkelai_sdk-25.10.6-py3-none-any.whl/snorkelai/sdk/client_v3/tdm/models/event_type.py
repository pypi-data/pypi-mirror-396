import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class EventType(StrEnum):
    CREATE = "create"
    DELETE = "delete"
    EXPORT = "export"
    READ = "read"
    UPDATE = "update"
