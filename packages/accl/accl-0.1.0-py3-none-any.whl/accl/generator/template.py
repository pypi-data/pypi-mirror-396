from __future__ import annotations

from typing import Any, Dict, List

from accl.schemas.chart import ChartQuestionContext
from accl.schemas.datatable import DataTableQuestionContext
from accl.schemas.angle import AngleQuestionContext
from accl.llm.base import BaseLLM
from accl.generator.qgen import generate_questions


def generate_chart_questions_with_llm(
    context: Dict[str, List[ChartQuestionContext]],
    model: BaseLLM,
    count: int = 1,
    prompt_key: str = "default_chart_prompt",
    template_type: str = "chart",
    meta_cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate LLM questions for each chart context in ``context["charts"]``.

    This is a thin wrapper around
    :func:`accl.generator.qgenerator.generate_questions` that fixes the
    context key and default prompt key for chart templates.
    """
    return generate_questions(
        context=context,
        context_key="charts",
        model=model,
        count=count,
        prompt_key=prompt_key,
        template_type=template_type,
        meta_cfg=meta_cfg,
    )

def generate_datatable_questions_with_llm(
    context: Dict[str, List[DataTableQuestionContext]],
    model: BaseLLM,
    count: int = 1,
    prompt_key: str = "default_datatable_prompt",
    template_type: str = "datatable",
    meta_cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate LLM questions for each datatable context in
    ``context["data_tables"]``.

    This is a thin wrapper around
    :func:`accl.generator.qgenerator.generate_questions` that fixes the
    context key and default prompt key for data-table templates.
    """
    return generate_questions(
        context=context,
        context_key="data_tables",
        model=model,
        count=count,
        prompt_key=prompt_key,
        template_type=template_type,
        meta_cfg=meta_cfg,
    )


def generate_angle_questions_with_llm(
    context: Dict[str, List[AngleQuestionContext]],
    model: BaseLLM,
    count: int = 1,
    prompt_key: str = "default_angle_prompt",
    template_type: str = "angle",
    meta_cfg: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """
    Generate LLM questions for each angle context in
    ``context["angles"]`` (or whatever key your ctxbuilder uses).
    """
    return generate_questions(
        context=context,
        context_key="angles",
        model=model,
        count=count,
        prompt_key=prompt_key,
        template_type=template_type,
        meta_cfg=meta_cfg,
    )