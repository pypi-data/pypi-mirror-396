import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class SvcSourceType(StrEnum):
    USER = "user"
    MACHINE = "machine"
    MODEL = "model"
    USERINPUT = "userinput"
    AGGREGATION = "aggregation"


class ModelSourceMetadata(BaseModel):
    model_name: str
    model_uid: Optional[int] = None
    model_description: Optional[str] = None
    model_metadata: dict = Field(default_factory=dict)
