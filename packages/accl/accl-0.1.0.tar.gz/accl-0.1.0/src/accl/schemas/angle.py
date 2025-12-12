from __future__ import annotations

from typing import List
from pydantic import BaseModel, conint

from accl.schemas.base import BasePayload, TemplateType, QuestionMeta


class AnglePayload(BasePayload):
    """
    Payload for a single angle-based question.

    This is analogous to ChartPayload but much simpler.
    """

    template_type: TemplateType = TemplateType.ANGLE

    # Angle in degrees (0–360)
    angle_degrees: conint(ge=0, le=360)

    # Visibility flags
    show_inner_value: bool = True
    show_inner_arc: bool = True
    show_outer_value: bool = True
    show_outer_arc: bool = True


class AngleQuestionContext(BaseModel):
    """
    What you pass into the LLM *per angle diagram*:
      - meta: who/where (same pattern as ChartQuestionContext)
      - payload: the angle itself
    """

    meta: QuestionMeta
    payload: AnglePayload


if __name__ == "__main__":
    payload = AnglePayload(
        angle_degrees=120,
        show_inner_value=True,
        show_inner_arc=True,
        show_outer_value=False,
        show_outer_arc=True,
    )

    print(payload)
    print("---" * 20)
