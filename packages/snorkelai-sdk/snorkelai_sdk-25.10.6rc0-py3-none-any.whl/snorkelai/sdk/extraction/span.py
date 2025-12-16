from enum import Enum
from typing import List, NamedTuple, Optional

# We use dashes in the SPAN_TOKEN instead of brackets/braces/underscores to keep it
# as a single token when tokenized by spacy/sklearn
SPAN_TOKEN = "-SPAN-"


class FlatSpanCols(Enum):
    DATAPOINT_UID = "context_uid"
    CHAR_START = "char_start"
    CHAR_END = "char_end"
    LABEL = "label"

    @staticmethod
    def get_columns() -> List[str]:
        return [x.value for x in FlatSpanCols]


# Group specially named fields into one object for ease of importing and extra clarity
class SpanCols:
    CONTEXT_UID = "context_uid"
    SPAN_FIELD = "span_field"
    SPAN_FIELD_VALUE_HASH = "span_field_value_hash"
    CHAR_START = "char_start"
    CHAR_END = "char_end"
    SPAN_TEXT = "span_text"
    INITIAL_LABEL = "initial_label"
    NORMALIZED_SPAN = "normalized_span"
    SPAN_PREVIEW = "span_preview"
    SPAN_PREVIEW_OFFSET = "span_preview_offset"
    SPAN_ENTITY = "span_entity"
    CONTEXT_SPANS = "context_spans"
    LEFT_CONTEXT = "left_context"
    RIGHT_CONTEXT = "right_context"
    SPANS = "spans"


class Span(NamedTuple):
    """A candidate consisting of a single span

    Parameters
    ----------
    context_uid:
        The uid of the context from which the candidate was extracted
    span_field:
        The name of the field that the span is extracted from
    span_field_value_hash:
        The hash of the value of the field that the span is extracted from,
        which is used to uniquely identify a span
    char_start:
        The index of the first character of the span for this candidate
    char_end:
        The index of the last character of the span for this candidate
    span_text:
        The text of the span (extracted from the context using char_start, char_end)
    initial_label:
        The label assigned to a span at creation time (if available)
        After initial upload, the label for a Span comes from TDM rather than the
        instance itself.
    span_entity:
        The entity linked to the span_text

    Thus, context[span_field[char_start, char_end + 1] contains the text of the span.

    """

    context_uid: int
    span_field: str
    span_field_value_hash: str
    char_start: int
    char_end: int
    span_text: str
    initial_label: int = -1
    span_entity: Optional[str] = None
