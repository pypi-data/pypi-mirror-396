import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class DatasetTransformConfigTypes(StrEnum):
    ANNOTATION_FILTER_SCHEMA = "annotation_filter_schema"
    ANNOTATOR_AGREEMENT_FILTER_SCHEMA = "annotator_agreement_filter_schema"
    ANNOTATOR_FILTER_SCHEMA = "annotator_filter_schema"
    CLUSTER_FILTER_SCHEMA = "cluster_filter_schema"
    COMMENT_FILTER_SCHEMA = "comment_filter_schema"
    CRITERIA_FILTER_SCHEMA = "criteria_filter_schema"
    DATASET_BATCH_SORTER = "dataset_batch_sorter"
    DATASET_COMBINER = "dataset_combiner"
    FIELD_FILTER_SCHEMA = "field_filter_schema"
    FILTER_CONDITION = "filter_condition"
    FILTER_GRAPH = "filter_graph"
    FILTER_SCHEMA = "filter_schema"
    FILTER_STRING = "filter_string"
    FIRST_N = "first_n"
    FIRST_N_TRACES = "first_n_traces"
    GROUND_TRUTH_FILTER_SCHEMA = "ground_truth_filter_schema"
    INDEX_PROVENANCE = "index_provenance"
    MARGIN_DISTANCE_FILTER_SCHEMA = "margin_distance_filter_schema"
    MODEL_FILTER_SCHEMA = "model_filter_schema"
    NATURAL_SORTER = "natural_sorter"
    SLICE_FILTER_SCHEMA = "slice_filter_schema"
    STATUS_FILTER_SCHEMA = "status_filter_schema"
    STUDIO_DATASET_SORTER = "studio_dataset_sorter"
    TEMPLATE_FILTER_SCHEMA = "template_filter_schema"
    VDS_SORTER = "vds_sorter"
