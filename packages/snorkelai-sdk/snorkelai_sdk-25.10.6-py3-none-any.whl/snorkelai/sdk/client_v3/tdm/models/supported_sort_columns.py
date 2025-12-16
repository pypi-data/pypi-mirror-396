import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class SupportedSortColumns(StrEnum):
    DATE_CREATED = "date_created"
    LABEL = "label"
    SOURCE_NAME = "source_name"
