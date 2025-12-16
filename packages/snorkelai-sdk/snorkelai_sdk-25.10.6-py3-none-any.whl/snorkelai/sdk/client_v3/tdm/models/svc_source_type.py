import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class SvcSourceType(StrEnum):
    AGGREGATION = "aggregation"
    MACHINE = "machine"
    MODEL = "model"
    USER = "user"
    USERINPUT = "userinput"
