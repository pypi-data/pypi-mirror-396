import json
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator

OperatorId = int


class OperatorInitConfig(BaseModel):
    """Data needed to initialize an operator."""

    op_type: str
    op_config: Dict[str, Any]
    op_asset: Optional[Dict[str, Any]] = (
        None  # None only when a custom operator class is used
    )
    op_impl_version: int = 0

    # Populators written out before https://github.com/snorkel-ai/strap/pull/30947
    # have "str" at op_asset. We decompile and migrate this to the new format for backcompat.
    @field_validator("op_asset", mode="before")
    @classmethod
    def decompile_op_asset(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        return v

    def __str__(self) -> str:
        # op configs can be very long, so we truncate to avoid log spam
        truncated_op_config = {
            k: f"{str(v)[:1000]}..." for k, v in self.op_config.items()
        }
        return json.dumps(
            {
                "op_type": self.op_type,
                "op_config": truncated_op_config,
                "op_asset": self.op_asset,
                "op_impl_version": self.op_impl_version,
            }
        )


class OperatorConfig(OperatorInitConfig):
    input_ids: List[OperatorId]
    is_output: bool = False


# Define Workflow-related constants
INPUT_NODE_ID = -1
INPUT_NODE_TYPE = "_input"

WorkflowConfig = Dict[OperatorId, OperatorConfig]


# Define Preprocessing-related constants
SKIPPED_DATAPOINTS_HEADER = ["skipped_datapoint", "error_msg"]
PREPROCESSING_ISSUES_HEADER = ["skipped_datapoint", "error_msg", "node", "check_type"]


class PreprocessingCheckType(StrEnum):
    PARSER_ERROR = "parser error"
    DOCUMENT_SIZE = "document size"
