from __future__ import annotations
from typing import Any, Callable, Tuple

from accl.ctxbuild.dtctx_builder import build_datatable_context
from accl.ctxbuild.chart_ctxbuilder import build_chart_context
from accl.ctxbuild.angle_ctxbuilder import build_angle_context

from accl.generator.template import generate_datatable_questions_with_llm, generate_chart_questions_with_llm, generate_angle_questions_with_llm

from accl.render.datatable_render import render_datatable_payload
from accl.render.chart_render import render_chart_payload
from accl.render.angle_render import render_angle_payload 

BuildContextFn = Callable[[dict, dict], dict]
GeneratorFn = Callable[..., list]
RenderFn = Callable[[Any, str, str, int], str]


def get_template_handler(template_type: str, model) -> Tuple[BuildContextFn, GeneratorFn, str, RenderFn | None]:
    """
    Return (build_context_fn, generator_fn, batch_key, render_fn_or_None)
    based on template_type.
    """

    if template_type == "data_table":
        return (
            lambda cfg, meta: build_datatable_context(cfg, meta),
            generate_datatable_questions_with_llm,
            "data_tables",
            lambda ctx_item, template_name, meta_key, idx: render_datatable_payload(
                ctx_item.payload,
                filename=f"{template_name}__{meta_key}_{idx}.png",
            ),
        )

    if template_type == "chart":
        return (
            lambda cfg, meta: build_chart_context(cfg, meta, model),
            generate_chart_questions_with_llm,
            "charts",
            lambda ctx_item, template_name, meta_key, idx: render_chart_payload(
                ctx_item.payload,
                filename=f"{template_name}__{meta_key}_{idx}.png",
            ),
        )

    if template_type == "angle":
        return (
            lambda cfg, meta: build_angle_context(cfg, meta),
            generate_angle_questions_with_llm,
            "angles",
            lambda ctx_item, template_name, meta_key, idx: render_angle_payload(
                ctx_item.payload,
                filename=f"{template_name}__{meta_key}_{idx}.png",
            ),
        )

    raise ValueError(f"Unsupported template_type: {template_type}")
