import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class NotificationType(StrEnum):
    COMMENT_TAG = "COMMENT_TAG"
    COMMIT_GT = "COMMIT_GT"
    COMPLETE_BATCH_ANNOTATION = "COMPLETE_BATCH_ANNOTATION"
    COMPLETE_LONG_RUNNING_LF = "COMPLETE_LONG_RUNNING_LF"
    COMPLETE_MODEL_TRAINING_JOB = "COMPLETE_MODEL_TRAINING_JOB"
