from typing import Dict, List, Type

from snorkelai.sdk.utils.datapoint import (
    DatapointType,
    DocDatapoint,
    EntityDatapoint,
)


class TaskTypes:
    CLASSIFICATION = "classification"
    MULTILABEL_CLASSIFICATION = "multilabel_classification"
    TEXT_EXTRACTION = "text_extraction"
    TEXT_ENTITY_CLASSIFICATION = "text_entity_classification"
    SEQUENCE_TAGGING = "sequence_tagging"
    APPLICATION = "Application"
    ANOMALY_DETECTION = "anomaly_detection"
    WORD_CLASSIFICATION = "word_classification"


class NodeTypes:
    CLASSIFICATION = "ClassificationNode"
    MULTILABEL_CLASSIFICATION = "MultilabelClassificationNode"
    TEXT_EXTRACTION = "ExtractionNode"
    TEXT_ENTITY_CLASSIFICATION = "EntityClassificationNode"
    ANOMALY_DETECTION = "AnomalyDetectionNode"
    SEQUENCE_TAGGING = "SequenceTaggingNode"
    IMAGE_CLASSIFICATION = "ImageClassificationNode"
    MULTILABEL_IMAGE_CLASSIFICATION = "MultilabelImageClassificationNode"
    LLM_FINE_TUNING_NODE = "LLMFineTuningNode"


TASK_TO_CONTEXT_DATAPOINT_TYPE = {
    TaskTypes.CLASSIFICATION: None,
    TaskTypes.MULTILABEL_CLASSIFICATION: None,
    TaskTypes.SEQUENCE_TAGGING: None,
    TaskTypes.TEXT_EXTRACTION: DocDatapoint,
    TaskTypes.TEXT_ENTITY_CLASSIFICATION: EntityDatapoint,
    TaskTypes.APPLICATION: None,
    TaskTypes.WORD_CLASSIFICATION: DocDatapoint,
}

TASK_TO_ADDITIONAL_DATAPOINT_TYPES: Dict[str, List[Type[DatapointType]]] = {
    TaskTypes.CLASSIFICATION: [],
    TaskTypes.MULTILABEL_CLASSIFICATION: [],
    TaskTypes.SEQUENCE_TAGGING: [],
    TaskTypes.TEXT_EXTRACTION: [],
    TaskTypes.TEXT_ENTITY_CLASSIFICATION: [EntityDatapoint],
    TaskTypes.APPLICATION: [],
}

TASK_TYPE_TO_TEMPLATE_ID = {
    TaskTypes.CLASSIFICATION: "clf",
    TaskTypes.MULTILABEL_CLASSIFICATION: "multilabel-clf",
    TaskTypes.TEXT_EXTRACTION: "te",
    TaskTypes.TEXT_ENTITY_CLASSIFICATION: "tec",
    TaskTypes.SEQUENCE_TAGGING: "seq",
    TaskTypes.ANOMALY_DETECTION: "tsad",
}
