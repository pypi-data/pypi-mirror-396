import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class FilterTransformFilterTypes(StrEnum):
    ANNOTATION = "annotation"
    ANNOTATION_TASK_ANNOTATOR = "annotation_task_annotator"
    ANNOTATION_TASK_DATA_POINT_STATUS = "annotation_task_data_point_status"
    ANNOTATOR_AGREEMENT = "annotator_agreement"
    CLUSTER = "cluster"
    COMMENT = "comment"
    CRITERIA = "criteria"
    FIELD = "field"
    GROUND_TRUTH = "ground_truth"
    MARGIN = "margin"
    MODEL = "model"
    SLICE = "slice"
    TEXT_TEMPLATE = "text_template"
