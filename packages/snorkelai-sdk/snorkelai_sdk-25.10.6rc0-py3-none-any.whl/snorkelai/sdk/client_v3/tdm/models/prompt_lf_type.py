import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class PromptLFType(StrEnum):
    PDF_TEXT2TEXT_EXTRACTOR = "pdf_text2text_extractor"
    PROMPT_DOCVQA = "prompt_docvqa"
    PROMPT_FREEFORM = "prompt_freeform"
    PROMPT_FREEFORM_MULTI_LABEL = "prompt_freeform_multi_label"
    PROMPT_QA = "prompt_qa"
    PROMPT_QA_FREEFORM = "prompt_qa_freeform"
    PROMPT_WORD_QA_FREEFORM = "prompt_word_qa_freeform"
