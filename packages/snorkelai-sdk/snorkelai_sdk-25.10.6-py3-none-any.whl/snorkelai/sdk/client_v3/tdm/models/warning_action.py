import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class WarningAction(StrEnum):
    REPLACE_MISSING_VALUES = "replace_missing_values"
