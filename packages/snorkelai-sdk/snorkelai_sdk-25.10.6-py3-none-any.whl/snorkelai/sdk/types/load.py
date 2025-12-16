import json
from enum import Enum
from typing import Any, Collection, Dict, List, Optional

from pydantic import BaseModel, Field, SecretStr, model_validator

Config = Dict[str, Any]
Configs = Collection[Config]


# DS schema version denotes the version number for the file format. We store
# files with specific format assumptions, e.g. indexed by context uid, or
# having a datapoint_uid col. When the format changes, this number should be incremented.
# Previous versions:
# 0: Default value. User generated file. Can have arbitrary format.
# 1: Files for non-classification tasks are indexed by the context uid, but it is named after the uid column in the docs dataframe.
# 2: Files have a DATAPOINT_UID_COL column.
# 3: Files are indexed by DATAPOINT_UID_COL and uid_col has to be DATAPOINT_UID_COL.
# 4. Files for preprocessed datasources are stored in the arrow-ipc format
UNPROCESSED_DS_SCHEMA_VERSION = 0
DATAPOINT_UID_DS_SCHEMA_VERSION = 2
CURRENT_DS_SCHEMA_VERSION = 4


ARROW_META_FILENAME = "arrow_meta"
PICKLE_META_FILENAME = "pickle_meta"
DELTA_LOG_DIRNAME = "_delta_log"
SNORKEL_SYSTEM_GENERATED_DIR = "snorkel-system-generated"
ENGINE_DATA_DIR = "snorkel-flow-engine-data"  # for backward compatibility
SNORKEL_DATASOURCES_DIR = "datasources"

UPLOADS_DIR = "uploads"
PARENT_DATASOURCE_DIR = "parent"
REPARTITIONED_DIR = "repartitioned"
WORKSPACE_DIR_PREFIX = "workspace-"
# for when each invidual datasource is stored in a separate directory
DATA_DIR_PREFIX = "data_"
# for when all datasources for a dataset are stored in a single directory
DATASET_DIR_PREFIX = "dataset_"


class SourceType(int, Enum):
    # Do not change values here without a migration since we store the ints in DB.
    CSV = 1
    PARQUET = 2
    SNOWFLAKE_QUERY = 3
    SQL_QUERY = 4
    # PICKLE = 5  Removed
    GOOGLE_BIGQUERY = 6
    ARROW_IPC = 7
    DATABRICKS_SQL = 8
    DELTA_TABLE = 9


class LoadConfig(BaseModel):
    path: str
    # ideally type would be mandatory, but deployments <= v0.69 try to access this
    # LoadConfig instead of the packaged one.
    type: SourceType = SourceType.ARROW_IPC
    col_types: Dict[str, str] = Field(default_factory=dict)
    uid_col: Optional[str] = None
    reader_kwargs: Dict[str, Any] = Field(default_factory=dict)
    credential_kwargs: Optional[SecretStr] = None
    parent_datasource_uid: Optional[int] = None
    context_datasource_uid: Optional[int] = None
    references: List[int] = Field(default_factory=list)
    ds_schema_version: int = (
        UNPROCESSED_DS_SCHEMA_VERSION  # Unprocessed means user file, with no special formatting.
    )
    data_connector_config_uid: Optional[int] = None

    # Validate if uid_col is set to DATAPOINT_UID_COL when ds_schema_version is 3 or higher
    @model_validator(mode="after")
    def validate_uid_col(self) -> "LoadConfig":
        if self.ds_schema_version >= 3 and self.uid_col != DATAPOINT_UID_COL:
            raise ValueError(
                f"uid_col has to be {DATAPOINT_UID_COL}, but received {self.uid_col}"
            )
        return self

    def dict(self, *args, **kwargs) -> Dict[str, Any]:  # type: ignore
        # yaml doesn't support loading enums, so we use the value instead
        load_config_dict = super().dict(*args, **kwargs)
        if "type" in load_config_dict:
            load_config_dict["type"] = load_config_dict["type"].value
        return load_config_dict

    def get_json_credential_kwargs_with_default(self) -> Dict[str, Any]:
        if self.credential_kwargs is not None:
            return json.loads(self.credential_kwargs.get_secret_value())
        return {}


LoadConfigs = Collection[LoadConfig]

TEMP_UID_COL = "__UID_COL"
DATAPOINT_UID_COL = "__DATAPOINT_UID"
DATASOURCE_UUID_COL = "__DATASOURCE_UUID"
TYPES_COL = "__types"
X_UID_COL = "x_uid"  # this is legacy, use DATAPOINT_UID_COL instead

ASSIGNEES_COL = "__ASSIGNEES"
ANNOTATION_TASK_STATUS_COL = "__STATUS"
