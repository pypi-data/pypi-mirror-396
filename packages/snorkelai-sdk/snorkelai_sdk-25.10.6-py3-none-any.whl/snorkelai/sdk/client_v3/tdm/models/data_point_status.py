import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DataPointStatus(StrEnum):
    COMPLETED = "COMPLETED"
    IN_ANNOTATION = "IN_ANNOTATION"
    NEEDS_ASSIGNEES = "NEEDS_ASSIGNEES"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
