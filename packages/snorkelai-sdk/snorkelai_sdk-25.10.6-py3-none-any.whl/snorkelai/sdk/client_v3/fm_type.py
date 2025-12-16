import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class FMType(StrEnum):
    TEXT2TEXT = "text2text"
    QA = "qa"
    DOCVQA = "docvqa"

    def __str__(self) -> str:
        return str(self.value)
