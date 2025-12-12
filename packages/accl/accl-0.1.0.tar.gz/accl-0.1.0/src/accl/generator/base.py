from __future__ import annotations
 
from typing import Dict, List, Any, Union

from pydantic import BaseModel, field_validator

class LLMGeneratedQuestion(BaseModel):
    """
    Same structure as in model_datatable.py.
    You can also import this from there if you prefer.
    """
    code: str
    template_type: str
    answer_format: str
    question_text: str
    options: List[str] | None = None
    correct_answer: Union[str, int, float, bool, List[str], List[int], List[float]] | None = None

    @field_validator("options", mode="before")
    def coerce_options_to_str(cls, v):
        """
        Allow the LLM to return numeric options (e.g. [28, 332, 360, 180])
        and coerce everything to strings.
        """
        if v is None:
            return []
        if not isinstance(v, list):
            raise TypeError("options must be a list")
        return [str(item) for item in v]