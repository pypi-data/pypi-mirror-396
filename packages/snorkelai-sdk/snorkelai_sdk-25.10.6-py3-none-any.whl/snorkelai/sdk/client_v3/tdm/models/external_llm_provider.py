import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class ExternalLLMProvider(StrEnum):
    ANTHROPIC = "anthropic"
    AZURE_ML = "azure_ml"
    AZURE_OPENAI = "azure_openai"
    BEDROCK = "bedrock"
    CUSTOM_INFERENCE_SERVICE = "custom_inference_service"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    VERTEXAI_LM = "vertexai_lm"
