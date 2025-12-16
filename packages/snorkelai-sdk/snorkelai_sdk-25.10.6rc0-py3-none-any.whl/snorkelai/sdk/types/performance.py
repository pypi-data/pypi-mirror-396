from typing import Optional

from pydantic import BaseModel, field_validator


class Performance(BaseModel):
    @field_validator("peak_memory_mb", mode="before")
    def coerce_peak_memory(cls, v: int) -> int:
        return int(v)

    @field_validator("compute_time_secs", mode="before")
    def coerce_compute_time(cls, v: int) -> int:
        return int(v)

    @field_validator("gpu_peak_memory_mb", mode="before")
    def maybe_coerce_gpu_peak_memory(cls, v: int) -> int:
        if v is not None:
            return int(v)

    compute_time_secs: int
    peak_memory_mb: int
    gpu_peak_memory_mb: Optional[int] = None
