from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any

from tqdm import tqdm

from accl.llm.gemini import GeminiLLM
from accl.utils.token_logger import TokenLogger
from accl.utils.savejson import save_questions_to_json
from accl.pipeline.handler import get_template_handler

logger = logging.getLogger("pipeline")


def run_single_template_meta(
    *,
    template_name: str,
    cfg: Dict[str, Any],
    meta_key: str,
    meta_cfg_map: Dict[str, Dict[str, Any]],
    model_name: str,
    google_client,
) -> None:
    """
    Run the full pipeline for a single (template_name, meta_key) pair:
      - build contexts
      - render images
      - generate questions with LLM
      - save questions JSON
      - save token log JSON/CSV
    """

    topic_meta_cfg = meta_cfg_map[meta_key]
    prompt_key = topic_meta_cfg.get("prompt_key", "default_prompt")

    run_id = f"{template_name}__{meta_key}"
    logger.info(f"🔥 Starting run: {run_id}")

    token_logger = TokenLogger(run_id=run_id)
    model = GeminiLLM(
        model_name=model_name,
        client=google_client,
        token_logger=token_logger,
    )

    template_type: str = cfg["template_type"]
    build_context, generator, batch_key, render_fn = get_template_handler(template_type, model)

    batch_size = cfg["batch_size"]
    questions_per_batch = cfg["questions_per_batch"]
    base_filename = cfg["filename"]

    # Add run_id to filename to avoid overwrites
    questions_filename = f"{Path(base_filename).stem}__{run_id}.json"

    # 1) Build context
    context = build_context(cfg, topic_meta_cfg)
    items = context[batch_key]
    num_items = len(items)

    logger.info(
        f"[{run_id}] Context built for template_type={template_type}, items={num_items}"
    )

    # 2) Render images
    if render_fn is not None:
        for idx, ctx_item in enumerate(items, start=1):
            img_path = render_fn(ctx_item, template_name, meta_key, idx)
            logger.info(f"[{run_id}] Rendered {template_type} {idx} → {img_path}")

    # 3) Generate LLM questions in batches
    all_questions = []
    num_batches = (num_items + batch_size - 1) // batch_size

    for batch_idx, start in enumerate(
        tqdm(
            range(0, num_items, batch_size),
            desc=f"Generating {run_id} questions",
            unit="batch",
            total=num_batches,
        )
    ):
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

    # 4) Save questions for this run
    save_questions_to_json(
        questions=all_questions,
        filename=questions_filename,
        template=run_id,
    )
    logger.info(f"[{run_id}] 💾 Saved questions → {questions_filename}")

    # 5) Export token logs for this run
    json_log = token_logger.export_json("reports")
    csv_log = token_logger.export_csv("reports")
    logger.info(f"[{run_id}] 📊 Token usage logs:\n- {json_log}\n- {csv_log}")


def run_all_templates(
    *,
    templates_cfg: Dict[str, Dict[str, Any]],
    meta_cfg_map: Dict[str, Dict[str, Any]],
    model_name: str,
    google_client,
    run_plan: Dict[str, list],
) -> None:
    """
    Orchestrates running all templates across their planned meta_keys (subjects/years).
    """

    for template_name, cfg in templates_cfg.items():
        if not cfg.get("enabled", True):
            continue

        # Determine which meta_keys to run for this template
        planned_meta_keys = run_plan.get(template_name, [])
        if not planned_meta_keys:
            logger.warning(
                f"No meta_keys found in RUN_PLAN for template '{template_name}', skipping."
            )
            continue
        # breakpoint()
        for meta_key in planned_meta_keys:
            run_single_template_meta(
                template_name=template_name,
                cfg=cfg,
                meta_key=meta_key,
                meta_cfg_map=meta_cfg_map,
                model_name=model_name,
                google_client=google_client,
            )

    logger.info("✅ All planned runs completed.")
