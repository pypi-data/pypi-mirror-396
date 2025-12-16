import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class LLMType(StrEnum):
    DOC_VQA = "doc_vqa"
    PDF_TEXT2TEXT_EXTRACTOR = "pdf_text2text_extractor"
    QA = "qa"
    RAG_PROMPT_ENRICHMENT_DOC_CLS_PREDICTOR = "rag_prompt_enrichment_doc_cls_predictor"
    RAG_PROMPT_ENRICHMENT_SEQ_TAG_PREDICTOR = "rag_prompt_enrichment_seq_tag_predictor"
    TEXT2TEXT = "text2text"
    TEXT2TEXT_MULTI_LABEL = "text2text_multi_label"
    TEXT2TEXT_QA = "text2text_qa"
    WORD_TEXT2TEXT_QA = "word_text2text_qa"
