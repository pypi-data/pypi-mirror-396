from __future__ import annotations

from typing import Dict, List
import random

from accl.ctxbuild.base import BaseContextBuilder
from accl.schemas.base import (
    QuestionMeta,
    TemplateType,
)
from accl.schemas.angle import AnglePayload, AngleQuestionContext


class AngleContextBuilder(BaseContextBuilder):
    template_type = TemplateType.ANGLE

    def build(
        self,
        *,
        angle_degrees: int,
        show_inner_value: bool = True,
        show_inner_arc: bool = True,
        show_outer_value: bool = True,
        show_outer_arc: bool = True,
    ) -> AnglePayload:
        """
        Create an AnglePayload from the given parameters.
        """
        payload = AnglePayload(
            angle_degrees=angle_degrees,
            show_inner_value=show_inner_value,
            show_inner_arc=show_inner_arc,
            show_outer_value=show_outer_value,
            show_outer_arc=show_outer_arc,
        )
        return payload


def choose_visibility(angle_params: dict) -> Dict[str, bool]:
    """
    Decide which parts of the angle diagram are visible.

    Config example:

      angle_params:
        randomize_visibility: true

    You can extend this later (e.g. specific modes).
    """
    randomize_visibility = angle_params.get("randomize_visibility", True)

    if not randomize_visibility:
        return {
            "show_inner_value": True,
            "show_inner_arc": True,
            "show_outer_value": True,
            "show_outer_arc": True,
        }

    show_inner_value = random.choice([True, False])
    show_inner_arc = random.choice([True, False])
    show_outer_value = random.choice([True, False])
    show_outer_arc = random.choice([True, False])

    # Ensure at least one value label is visible so questions are meaningful
    if not (show_inner_value or show_outer_value):
        show_inner_value = True

    # You can also enforce at least one arc visible if you like:
    if not (show_inner_arc or show_outer_arc):
        show_inner_arc = True

    return {
        "show_inner_value": show_inner_value,
        "show_inner_arc": show_inner_arc,
        "show_outer_value": show_outer_value,
        "show_outer_arc": show_outer_arc,
    }


def build_angle_context(
    template_cfg: dict,
    meta_cfg: dict,
) -> Dict[str, List[AngleQuestionContext]]:
    """
    Generic builder for ANGLE contexts.

    template_cfg comes from template_config.yaml under templates.<template_name>.
    meta_cfg comes from question_meta_configs.<meta_key>.

    Expected example in template_config.yaml:

      templates:
        angle_basic:
          enabled: true
          template_type: "angle"
          batch_key: "angles"
          batch_size: 8
          questions_per_batch: 2
          filename: "angle_basic_questions.json"

          angle_params:
            num_angles: 16
            min_degrees: 10
            max_degrees: 360
            randomize_visibility: true
    """
    # breakpoint()
    angle_params: dict = template_cfg["angle_params"]
    num_angles: int = template_cfg.get("num_angles", 10)

    min_deg: int = angle_params.get("min_degrees", 10)
    max_deg: int = angle_params.get("max_degrees", 360)

    builder = AngleContextBuilder()
    contexts: List[AngleQuestionContext] = []

    for i in range(num_angles):
        angle_degrees = random.randint(min_deg, max_deg)

        vis_flags = choose_visibility(angle_params)

        payload = builder.build(
            angle_degrees=angle_degrees,
            **vis_flags,
        )

        meta = QuestionMeta(
            id=f'{meta_cfg["id_prefix"]}{i+1}',
            year=meta_cfg["year"],
            subject=meta_cfg["subject"],
            category=meta_cfg["category"],
            question_name=f'{meta_cfg["question_name_prefix"]}{i+1}',
            expected_time_secs=meta_cfg["expected_time_secs"],
        )

        contexts.append(AngleQuestionContext(meta=meta, payload=payload))

    return {"angles": contexts}


