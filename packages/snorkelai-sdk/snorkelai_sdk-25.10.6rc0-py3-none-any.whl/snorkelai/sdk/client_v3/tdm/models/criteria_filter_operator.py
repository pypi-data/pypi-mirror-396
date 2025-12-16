import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class CriteriaFilterOperator(StrEnum):
    ABSENT = "absent"
    PRESENT = "present"
    VALUE_2 = "=="
    VALUE_3 = ">"
    VALUE_4 = "<"
    VALUE_5 = ">="
    VALUE_6 = "<="
