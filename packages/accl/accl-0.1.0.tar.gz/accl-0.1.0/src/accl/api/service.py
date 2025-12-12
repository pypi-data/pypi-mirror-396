# src/api/service.py

from __future__ import annotations

import logging
from typing import Any, Dict, List

from google import genai

from config import settings
from accl.utils.config_loader import load_model_config, load_template_config
from accl.pipeline.handler import get_template_handler
from accl.llm.gemini import GeminiLLM
from accl.api.schemas import TemplateRunResult, QuestionRecord
from accl.utils.token_logger import TokenLogger
from accl.api.storage import save_run_json, get_reports_dir
import logging

logger= logging.getLogger("api.service")


def run_single_template_meta_in_memory(
    *,
    template_name: str,
    cfg: Dict[str, Any],
    meta_key: str,
    meta_cfg_map: Dict[str, Dict[str, Any]],
    model_name: str,
    google_client: genai.Client,
) -> TemplateRunResult:
    """
    In-memory version of the pipeline for a single (template_name, meta_key) pair.

    It:
      - builds contexts
      - optionally renders images
      - generates questions with the LLM
      - returns a TemplateRunResult (no files written)
    """

    topic_meta_cfg = meta_cfg_map[meta_key]
    prompt_key = topic_meta_cfg.get("prompt_key", "generic_question_prompt")

    run_id = f"{template_name}__{meta_key}"
    logger.info(f"[API] Starting run: {run_id}")
    
    token_logger = TokenLogger(run_id=run_id)
    # Model for this run (shares underlying google_client)
    model = GeminiLLM(
        model_name=model_name,
        client=google_client,
        token_logger=token_logger
    )

    template_type: str = cfg["template_type"]
    build_context, generator, batch_key, render_fn = get_template_handler(
        template_type, model
    )

    batch_size: int = cfg["batch_size"]
    questions_per_batch: int = cfg["questions_per_batch"]

    # 1) Build context
    context = build_context(cfg, topic_meta_cfg)
    items = context[batch_key]
    num_items = len(items)

    logger.info(
        f"[API][{run_id}] Context built for template_type={template_type}, items={num_items}"
    )

    # 2) Render images (optional, but we keep it for now)
    if render_fn is not None:
        for idx, ctx_item in enumerate(items, start=1):
            img_path = render_fn(ctx_item, template_name, meta_key, idx)
            logger.info(f"[API][{run_id}] Rendered {template_type} {idx} → {img_path}")

    # 3) Generate questions in batches
    all_questions: List[Dict[str, Any]] = []
    if num_items == 0:
        logger.warning(f"[API][{run_id}] No items to generate questions for.")
    else:
        num_batches = (num_items + batch_size - 1) // batch_size

        for batch_idx, start in enumerate(range(0, num_items, batch_size)):
            model.set_context(template_name=run_id, batch_id=batch_idx)

            batch_context = {
                key: value[start : start + batch_size]
                for key, value in context.items()
            }

            batch_results = generator(
                batch_context,
                model,
                count=questions_per_batch,
                prompt_key=prompt_key,
                template_type=template_type,
                meta_cfg=topic_meta_cfg,
            )
            all_questions.extend(batch_results)

    # 4) Wrap into TemplateRunResult
    question_records = [
        QuestionRecord(
            meta=q["meta"],
            template=q["template"],
            llm_question=q["llm_question"],
        )
        for q in all_questions
    ]

    run_result=  TemplateRunResult(
        template=run_id,
        questions=question_records,
    )
    
    # 5) Persist this run's JSON result into shared_temp/outputs
    json_path = save_run_json(run_id, run_result.model_dump())
    logger.info(f"[API][{run_id}] 💾 Saved run JSON → {json_path}")

    # 6) Export token logs into shared_temp/reports
    reports_dir = str(get_reports_dir())
    json_log = token_logger.export_json(reports_dir)
    csv_log = token_logger.export_csv(reports_dir)
    logger.info(f"[API][{run_id}] 📊 Token usage logs:\n- {json_log}\n- {csv_log}")

    return run_result


def run_plan_in_memory(run_plan: Dict[str, List[str]]) -> List[TemplateRunResult]:
    """
    Orchestrate running the given run_plan using the in-memory pipeline.

    run_plan format example:
      {
        "datatables": ["stat_prob_yr10", "measures_yr10"],
        "charts": ["patterns_relationships_sequences_yr10"],
        "angles": ["measures_yr10"]
      }
    """

    # Load template + meta configs
    template_cfg = load_template_config()
    templates_cfg: Dict[str, Dict[str, Any]] = template_cfg["templates"]
    meta_cfg_map: Dict[str, Dict[str, Any]] = template_cfg["question_meta_configs"]

    # Model config + Google client
    model_cfg = load_model_config()
    # Adjust this indexing based on your actual config structure
    model_name = model_cfg.get("model", {}).get("name") or model_cfg.get("name")

    google_client = genai.Client(api_key=settings.GEMINI_API_KEY)

    results: List[TemplateRunResult] = []

    for template_name, meta_keys in run_plan.items():
        cfg = templates_cfg.get(template_name)
        if cfg is None:
            logger.warning(
                f"[API] Template '{template_name}' not found in templates_cfg; skipping."
            )
            continue

        for meta_key in meta_keys:
            if meta_key not in meta_cfg_map:
                logger.warning(
                    f"[API] meta_key '{meta_key}' not found in question_meta_configs; skipping."
                )
                continue

            result = run_single_template_meta_in_memory(
                template_name=template_name,
                cfg=cfg,
                meta_key=meta_key,
                meta_cfg_map=meta_cfg_map,
                model_name=model_name,
                google_client=google_client,
            )
            results.append(result)

    return results
