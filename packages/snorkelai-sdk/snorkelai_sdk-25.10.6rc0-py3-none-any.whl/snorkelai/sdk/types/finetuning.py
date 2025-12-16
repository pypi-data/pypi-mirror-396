import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator

from snorkelai.sdk.utils.hashing import consistent_hash


class FineTuningColumnType(StrEnum):
    INSTRUCTION = "instruction"
    CONTEXT = "context"
    RESPONSE = "response"
    PROMPT_PREFIX = "prompt_prefix"


class ModelProviders(StrEnum):
    MISTRAL = "mistral"
    LLAMA = "llama"


class AnnotationStrategy(StrEnum):
    ACCEPT_REJECT = "accept_reject"
    RESPONSE_RANKING = "response_ranking"


class FinetuningProvider(StrEnum):
    AWS_SAGEMAKER = "sagemaker"


class LLMFineTuningLabelingConfig(BaseModel):
    enable_free_response: bool = False
    annotation_strategy: AnnotationStrategy = AnnotationStrategy.ACCEPT_REJECT
    label_map: Dict[str, Any] = Field(
        default_factory=lambda: {"ACCEPT": 1, "REJECT": 0}
    )
    accept_label_value: int = Field(default=1)

    @field_validator("annotation_strategy")
    @classmethod
    def validate_annotation_strategy(cls, v: AnnotationStrategy) -> Any:
        if v != AnnotationStrategy.ACCEPT_REJECT:
            raise ValueError("Only ACCEPT_REJECT annotation strategy is supported")
        return v


REQUIRED_COLS = [FineTuningColumnType.INSTRUCTION]


class FineTuningDatasourceMetadata(BaseModel):
    source_uid: int


class FMFeatures(BaseModel):
    instructions: List[str]
    prompt_prefixes: List[str]
    contexts: List[str]
    prompt_template: str

    def get_hash(self) -> str:
        return str(consistent_hash(sorted(self.dict().items())))


class FTDoc(BaseModel):
    instructions: List[str]
    prompt_prefixes: List[str]
    contexts: List[str]
    responses: List[str]
    prompt_template: str
    source_uid: int

    def get_datapoint_uid(self) -> str:
        feature_hash = self.get_feature_hash()
        prediction_hash = self.get_prediction_hash()
        return f"{feature_hash}-{self.source_uid}-{prediction_hash}"

    def get_feature_hash(self) -> str:
        # Sort the lists to ensure hash is consistent
        return FMFeatures(
            instructions=sorted(self.instructions),
            contexts=sorted(self.contexts),
            prompt_prefixes=sorted(self.prompt_prefixes),
            prompt_template=self.prompt_template,
        ).get_hash()

    def get_prediction_hash(self) -> str:
        return str(consistent_hash(sorted(self.responses)))


class ExportFormat(StrEnum):
    JSONL = "jsonl"
