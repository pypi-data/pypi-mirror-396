from typing import Any, List, Optional

from pydantic import BaseModel


class SuggestionModel(BaseModel):
    msg: str
    key: Optional[str] = None
    lvl: int
    lf_names: Optional[List[str]] = None
    page: Optional[str] = None
    page_options: Optional[Any] = None
