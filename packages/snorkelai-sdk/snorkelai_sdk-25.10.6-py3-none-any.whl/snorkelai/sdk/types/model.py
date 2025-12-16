from enum import Enum


class ModelCols:
    PREDICTION_PROBABILITY = "probs"
    PREDICTION_INT = "preds"
    PREDICTION_STR = "preds_str"
    DECISION_FUNCTION = "decision_fn"


# Class used for aggregation token classification model predictions
class AggregationType(Enum):
    NONE: str = "none"
    FIRST: str = "first"
    AVERAGE: str = "average_confidence"
    MAX: str = "max_confidence"


class LayoutEncodingType(Enum):
    TOKEN: str = "token"  # Encoding for span token classification
    SEQUENCE: str = "sequence"  # Encoding for document classification
    WORD: str = "word"  # Encoding for word classification
