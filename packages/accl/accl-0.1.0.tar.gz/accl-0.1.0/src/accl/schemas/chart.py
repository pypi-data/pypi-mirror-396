# chartschema.py

from __future__ import annotations

from typing import List
from enum import Enum

from pydantic import BaseModel, conint, field_validator

from accl.schemas.base import BasePayload, TemplateType, QuestionMeta


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    # Later: SCATTER = "scatter", HISTOGRAM = "histogram", etc.


class ChartPayload(BasePayload):
    """
    Generic payload for chart-based questions.

    Works for line/bar/pie (and is extendable).
    """

    template_type: TemplateType = TemplateType.CHART

    chart_type: ChartType

    title: str
    x_label: str
    y_label: str

    # Categories / x-axis labels
    x_values: List[str]

    # Each series gets a name (used for legend)
    series_names: List[str]

    # 2D data:
    #   - outer length = number of series
    #   - inner length = number of x_values
    # Example for 2 series & 3 x_values:
    #   values = [
    #       [10, 20, 30],  # series 1
    #       [15, 25, 35],  # series 2
    #   ]
    values: List[List[conint(ge=0)]]
    show_legend: bool = True

    @field_validator("values")
    def validate_values(cls, v, info):
        """
        Ensure:
          - number of rows in `values` matches series_names
          - each row length matches x_values length
        """
        x_values = info.data.get("x_values")
        series_names = info.data.get("series_names")

        if series_names is not None and len(v) != len(series_names):
            raise ValueError(
                f"`values` has {len(v)} series rows, expected {len(series_names)} "
                f"to match `series_names`."
            )

        if x_values is not None:
            expected_len = len(x_values)
            for i, row in enumerate(v):
                if len(row) != expected_len:
                    raise ValueError(
                        f"`values` row {i} has length {len(row)}, "
                        f"expected {expected_len} to match `x_values`."
                    )

        return v


class ChartQuestionContext(BaseModel):
    """
    What you pass into the LLM *per chart*:
      - meta: who/where
      - payload: the chart itself

    LLM uses the chart payload to generate question text, options, etc.
    """
    meta: QuestionMeta
    payload: ChartPayload


if __name__ == "__main__":

    payload = ChartPayload(
        chart_type=ChartType.LINE,
        title="Homework Problems Solved During the Week",
        x_label="Day of the Week",
        y_label="Number of problems solved",
        x_values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        series_names=["Class A", "Class B"],
        values=[
            [5, 7, 8, 6, 9],   # Class A
            [4, 6, 7, 5, 8],   # Class B
        ],
    )

    print(payload)
    print("---"*100)
