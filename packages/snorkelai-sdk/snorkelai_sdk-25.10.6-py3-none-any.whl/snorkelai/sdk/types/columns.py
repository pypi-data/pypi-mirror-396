class ConvCols:
    """Base class that specifies Conversation columns."""

    # a json blob with utterances and speakers
    CONV_COL = "conversation_json"
    # raw text consisting of joined utterances (no speaker names)
    TEXT_COL = "conversation_text"
    # index for an utterance
    IDX_COL = "utterance_idx"
    # actual utterance text
    UTTERANCE = "utterance"
    # list of utterances in a conversation
    UTTERANCES = "utterances"
    # speaker for an utterance
    SPEAKER = "speaker"
    # dictionary which contains information about all speakers
    SPEAKERS = "speakers"
    # timestamp for an utterance
    TIMESTAMP = "timestamp"
    # metadata for an utterance
    METADATA = "metadata"
    # boolean representing whether utterances by a corresponding speaker
    # should be included for classification
    SHOULD_CLASSIFY = "should_classify"
    # label of an utterance
    UTTERANCE_LABEL = "utterance_label"
    # Spacy extracted entities within an utterance
    UTTERANCE_ENTITIES = "utterance_entities"
    # Default feature name for last_k_utterances
    # These features are added by default when using the app template
    LAST_5_UTTERANCES_SAME = "last_5_utterances_same"
    LAST_5_UTTERANCES_OTHER = "last_5_utterances_other"


class RelationClassificationCols:
    TEXT_BETWEEN = "text_between"
    TEXT_LEFT_OF_ENTITY1 = "text_left_of_entity1"
    TEXT_RIGHT_OF_ENTITY2 = "text_right_of_entity2"
    ENTITY_SPANS = "entity_spans"
    ENTITY_SPAN = "entity_span"


def tokenize_column(column: str) -> str:
    return f"tokenized_{column}"
