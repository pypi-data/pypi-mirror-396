import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class JobType(StrEnum):
    ADD_DATASET_GROUND_TRUTH = "add-dataset-ground-truth"
    ANALYZE_DATASOURCE = "analyze-datasource"
    ANALYZE_DATASOURCES_V2 = "analyze-datasources-v2"
    APPLY_LFS_WRAPPER = "apply-lfs-wrapper"
    CLEAN_DISK_LRU_CACHE = "clean-disk-lru-cache"
    COPY_LABEL_SCHEMA = "copy-label-schema"
    CREATE_BATCH_WITH_PROMPT_UID = "create-batch-with-prompt-uid"
    CREATE_DATASOURCE_CACHE = "create-datasource-cache"
    DELETE_DATASOURCE = "delete-datasource"
    DELETE_NODE = "delete-node"
    ERROR_ANALYSIS_CLUSTERING = "error-analysis-clustering"
    EVAL_APPLY_BENCHMARK_POPULATOR = "eval-apply-benchmark-populator"
    EVAL_CREATE_BENCHMARK_POPULATOR = "eval-create-benchmark-populator"
    EVAL_EXECUTE_CODE_EXECUTION = "eval-execute-code-execution"
    EVAL_GATHER_METRICS = "eval-gather-metrics"
    EVAL_UPDATE_METRICS = "eval-update-metrics"
    FETCH_DATASET_COLUMNS = "fetch-dataset-columns"
    FETCH_DATASET_COLUMN_TYPES = "fetch-dataset-column-types"
    GARBAGE_COLLECT_DATASET_APPLICATION = "garbage-collect-dataset-application"
    GARBAGE_COLLECT_DATASET_APPLICATION_NODES = (
        "garbage-collect-dataset-application-nodes"
    )
    GET_DATAFRAME = "get-dataframe"
    GET_UNIQUE_VALUES_IN_COLUMN = "get-unique-values-in-column"
    INGEST_AND_SWAP_DATASOURCE = "ingest-and-swap-datasource"
    INGEST_DATA = "ingest-data"
    LIST_AGGREGATED_SME_FEEDBACK_GROUND_TRUTH = (
        "list-aggregated-sme-feedback-ground-truth"
    )
    LIST_BACKUPS = "list-backups"
    NO_OP = "no-op"
    PEEK_DATASOURCE_COLUMNS = "peek-datasource-columns"
    PEEK_DATASOURCE_COLUMN_MAP = "peek-datasource-column-map"
    POSTPROCESS_MODEL = "postprocess-model"
    PREP_AND_INGEST_DATA = "prep-and-ingest-data"
    PREVIEW_DATA = "preview-data"
    PROMPT_FM = "prompt-fm"
    REFRESH_ACTIVE_DATASOURCES = "refresh-active-datasources"
    REMOVE_DATASET = "remove-dataset"
    RESTORE_BACKUP = "restore-backup"
    SET_ACTIVE_NODE_DATA = "set-active-node-data"
    TAKE_BACKUP = "take-backup"
    UPLOAD_STATIC_ASSETS = "upload-static-assets"
