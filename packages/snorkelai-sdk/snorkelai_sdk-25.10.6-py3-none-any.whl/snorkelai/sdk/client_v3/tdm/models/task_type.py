import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class TaskType(StrEnum):
    CANDIDATE_EXTRACTION = "candidate_extraction"
    CLASSIFICATION = "classification"
    ENTITY_CLASSIFICATION = "entity_classification"
    SEQUENCE_TAGGING = "sequence_tagging"
    WORD_CLASSIFICATION = "word_classification"
