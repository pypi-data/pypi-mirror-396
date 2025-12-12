# src/api/schemas.py

from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel


class RunPlanRequest(BaseModel):
    """
    Request body for the generation endpoint.

    Example:
    {
      "run_plan": {
        "datatables": ["stat_prob_yr10", "measures_yr10"],
        "charts": ["patterns_relationships_sequences_yr10"],
        "angles": ["measures_yr10"]
      }
    }
    """
    run_plan: Dict[str, List[str]]


class QuestionRecord(BaseModel):
    """
    Single generated question record:
      - meta: question metadata (id, year, category, ...)
      - template: the underlying payload (table/chart/angle)
      - llm_question: the question object produced by the LLM
    """
    meta: Dict[str, Any]
    template: Dict[str, Any]
    llm_question: Dict[str, Any]


class TemplateRunResult(BaseModel):
    """
    Result for a single (template_name, meta_key) run.

    Example "template" values:
      - "datatables__stat_prob_yr10"
      - "charts__patterns_relationships_sequences_yr10"
      - "angles__measures_yr10"
    """
    template: str
    questions: List[QuestionRecord]
