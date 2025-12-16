import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DatasetTransformType(StrEnum):
    ANNOTATION_TASK_ANNOTATOR_FILTER = "annotation_task_annotator_filter"
    ANNOTATION_TASK_FIELD_FILTER = "annotation_task_field_filter"
    ANNOTATION_TASK_STATUS_FILTER = "annotation_task_status_filter"
    BATCH_ANNOTATION_FILTER = "batch_annotation_filter"
    BATCH_ANNOTATOR_AGREEMENT_FILTER = "batch_annotator_agreement_filter"
    BATCH_COMMENT_FILTER = "batch_comment_filter"
    BATCH_FIELD_FILTER = "batch_field_filter"
    BATCH_GROUND_TRUTH_FILTER = "batch_ground_truth_filter"
    BATCH_SLICE_FILTER = "batch_slice_filter"
    BENCHMARK_ANNOTATION_FILTER = "benchmark_annotation_filter"
    BENCHMARK_ANNOTATOR_AGREEMENT_FILTER = "benchmark_annotator_agreement_filter"
    BENCHMARK_COMMENT_FILTER = "benchmark_comment_filter"
    BENCHMARK_CRITERIA_FILTER = "benchmark_criteria_filter"
    BENCHMARK_FIELD_FILTER = "benchmark_field_filter"
    BENCHMARK_GROUND_TRUTH_FILTER = "benchmark_ground_truth_filter"
    BENCHMARK_SLICE_FILTER = "benchmark_slice_filter"
    DATALOADER = "dataloader"
    DATASET_ANNOTATION_FILTER = "dataset_annotation_filter"
    DATASET_BATCH_SORTER = "dataset_batch_sorter"
    DATASET_COMBINER = "dataset_combiner"
    DATASET_COMMENT_FILTER = "dataset_comment_filter"
    DATASET_FIELD_FILTER = "dataset_field_filter"
    DATASET_GROUND_TRUTH_FILTER = "dataset_ground_truth_filter"
    DATASET_SLICE_FILTER = "dataset_slice_filter"
    DATASET_TEMPLATE_FILTER = "dataset_template_filter"
    FILTER_GRAPH = "filter_graph"
    FIRST_N = "first_n"
    FIRST_N_TRACES = "first_n_traces"
    MANUAL = "manual"
    NATURAL_SORTER = "natural_sorter"
    NODE_CLUSTER_FILTER = "node_cluster_filter"
    NODE_COMMENT_FILTER = "node_comment_filter"
    NODE_FIELD_FILTER = "node_field_filter"
    NODE_GROUND_TRUTH_FILTER = "node_ground_truth_filter"
    NODE_MARGIN_FILTER = "node_margin_filter"
    NODE_MODEL_FILTER = "node_model_filter"
    NODE_SLICE_FILTER = "node_slice_filter"
    STUDIO_DATASET_SORTER = "studio_dataset_sorter"
    TEXT_TEMPLATE = "text_template"
    VDS_SORTER = "vds_sorter"
