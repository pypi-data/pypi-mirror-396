# src/api/app.py

from __future__ import annotations

from typing import List
import logging
import sys
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from accl.api.schemas import RunPlanRequest, TemplateRunResult
from accl.api.service import run_plan_in_memory


# -------------------------------------------------------------------
# Configure global logging so all modules (pipeline, llm, renderer, API)
# actually emit logs to the console when run via uvicorn.
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("api")

app = FastAPI(
    title="ACCL Question Generation API",
    version="1.0.0",
    description="API to generate curriculum-aligned maths questions from chart/table/angle templates.",
)


@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "ok"}


@app.post(
    "/generate",
    response_model=List[TemplateRunResult],
    summary="Generate questions for a given run plan",
)
async def generate_questions(payload: RunPlanRequest):
    """
    Run the generation pipeline for the specified run_plan.

    Example request body:
    {
      "run_plan": {
        "datatables": ["stat_prob_yr10"],
        "charts": ["patterns_relationships_sequences_yr10"],
        "angles": ["measures_yr10"]
      }
    }

    Response is a list like:
    [
      {
        "template": "datatables__stat_prob_yr10",
        "questions": [
          {
            "meta": {...},
            "template": {...},
            "llm_question": {...}
          },
          ...
        ]
      },
      ...
    ]
    """
    results = run_plan_in_memory(payload.run_plan)
    return JSONResponse(content=[r.model_dump() for r in results])
