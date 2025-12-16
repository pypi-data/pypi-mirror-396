import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from typing import Any


class ConstValues(StrEnum):
    @classmethod
    def is_member(cls, s: str) -> bool:
        return s in cls._value2member_map_


class JobType(ConstValues):
    # Engine
    ANALYZE_DATASOURCE = "analyze-datasource"
    ANALYZE_DATASOURCES_V2 = "analyze-datasources-v2"
    ADD_DATASET_GROUND_TRUTH = "add-dataset-ground-truth"
    LIST_AGGREGATED_SME_FEEDBACK_GROUND_TRUTH = (
        "list-aggregated-sme-feedback-ground-truth"
    )
    INGEST_DATA = "ingest-data"
    DELETE_DATASOURCE = "delete-datasource"
    INGEST_AND_SWAP = "ingest-and-swap-datasource"
    PREP_AND_INGEST_DATA = "prep-and-ingest-data"
    PREVIEW_DATA = "preview-data"
    SET_ACTIVE_NODE_DATA = "set-active-node-data"
    CREATE_DATASOURCE_CACHE = "create-datasource-cache"
    PROMPT_FM = "prompt-fm"
    TAKE_BACKUP = "take-backup"
    RESTORE_BACKUP = "restore-backup"
    LIST_BACKUPS = "list-backups"
    REMOVE_DATASET = "remove-dataset"
    PEEK_DATASOURCE_COLUMNS = "peek-datasource-columns"
    FETCH_DATASET_COLUMN_TYPES = "fetch-dataset-column-types"
    PEEK_DATASOURCE_COLUMN_MAP = "peek-datasource-column-map"
    GARBAGE_COLLECT_DATASET_APPLICATION_NODES = (
        "garbage-collect-dataset-application-nodes"
    )
    GARBAGE_COLLECT_DATASET_APPLICATION = "garbage-collect-dataset-application"
    APPLY_LFS_WRAPPER = "apply-lfs-wrapper"
    DELETE_NODE = "delete-node"
    FETCH_DATASET_COLUMNS = "fetch-dataset-columns"
    REFRESH_ACTIVE_DATASOURCES = "refresh-active-datasources"
    POSTPROCESS_MODEL = "postprocess-model"
    GET_UNIQUE_VALUES_IN_COLUMN = "get-unique-values-in-column"
    CLEAN_DISK_LRU_CACHE = "clean-disk-lru-cache"
    COPY_LABEL_SCHEMA = "copy-label-schema"
    UPLOAD_STATIC_ASSETS = "upload-static-assets"
    GET_DATAFRAME = "get-dataframe"
    CREATE_BATCH_WITH_PROMPT_UID = "create-batch-with-prompt-uid"
    EVAL_UPDATE_METRICS = "eval-update-metrics"
    EVAL_GATHER_METRICS = "eval-gather-metrics"
    EVAL_APPLY_BENCHMARK_POPULATOR = "eval-apply-benchmark-populator"
    EVAL_CREATE_BENCHMARK_POPULATOR = "eval-create-benchmark-populator"
    EVAL_EXECUTE_CODE_EXECUTION = "eval-execute-code-execution"
    ERROR_ANALYSIS_CLUSTERING = "error-analysis-clustering"
    # N/A
    NO_OP = "no-op"


class JobState(ConstValues):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @classmethod
    def is_finished(cls, state: Any) -> bool:
        return state in {cls.COMPLETED, cls.FAILED, cls.CANCELLED}
