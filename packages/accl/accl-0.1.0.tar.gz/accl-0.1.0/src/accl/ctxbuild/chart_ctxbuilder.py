# src/ctxbuild/chart_ctxbuilder.py

from __future__ import annotations

from typing import Dict, List
import random

from accl.ctxbuild.base import BaseContextBuilder
from accl.schemas.base import (
    QuestionMeta,
    TemplateType,
)
from accl.schemas.chart import (
    ChartPayload,
    ChartQuestionContext,
    ChartType,
)
from accl.llm.base import BaseLLM
from accl.utils.prompt_loader import load_prompt


class ChartContextBuilder(BaseContextBuilder):
    """
    Build chart question payloads for CHART templates.

    This context builder converts high-level chart configuration
    (chart type, labels, categories, series metadata and numeric
    values) into a validated `ChartPayload` that can be used by
    downstream renderers and question generators.

    Attributes
    ----------
    template_type : TemplateType
        Template type for this context builder. Fixed to
        ``TemplateType.CHART`` so the pipeline can route chart
        templates to this builder.
    """

    template_type = TemplateType.CHART

    def build(
        self,
        chart_type: ChartType,
        title: str,
        x_label: str,
        y_label: str,
        x_values: List[str],
        series_names: List[str],
        values: List[List[int]],
        show_legend: bool = True,
    ) -> ChartPayload:
        """
        Construct and validate a `ChartPayload` instance.

        Parameters
        ----------
        chart_type : ChartType
            Type of chart to build (for example, ``ChartType.LINE``,
            ``ChartType.BAR`` or ``ChartType.PIE``).
        title : str
            Title to show above the chart.
        x_label : str
            Label for the x-axis.
        y_label : str
            Label for the y-axis.
        x_values : list of str
            Ordered category labels along the x-axis.
            Length determines the number of points per series.
        series_names : list of str
            Display names for each data series. Length must match
            the outer dimension of ``values``.
        values : list of list of int
            Numeric data for each series. ``values[i][j]`` is the
            value for series ``i`` at x-category ``j``. Each inner
            list must have length equal to ``len(x_values)``.
        show_legend : bool, optional
            Whether a legend should be displayed when rendering
            the chart, by default True.

        Returns
        -------
        ChartPayload
            A validated chart payload ready to be rendered or used
            to generate questions.

        Raises
        ------
        ValueError
            If any of the following conditions hold:

            * ``x_values`` is empty.
            * ``series_names`` is empty.
            * ``len(values) != len(series_names)``.
            * Any row in ``values`` has length different from
              ``len(x_values)``.
        """

        if not x_values:
            raise ValueError("`x_values` must contain at least one category")

        if not series_names:
            raise ValueError("`series_names` must contain at least one series")

        if len(values) != len(series_names):
            raise ValueError("`values` length must match number of `series_names`")

        for row in values:
            if len(row) != len(x_values):
                raise ValueError("Each row in `values` must match length of `x_values`")

        payload = ChartPayload(
            chart_type=chart_type,
            title=title,
            x_label=x_label,
            y_label=y_label,
            x_values=x_values,
            series_names=series_names,
            values=values,
            show_legend=show_legend,
        )
        return payload


def generate_scenarios_from_llm(
    llm: BaseLLM,
    chart_params: dict,
) -> List[Dict]:
    """
    Use the LLM to generate chart scenarios, using a prompt template
    loaded via `prompt_loader`.

    Expected config keys in chart_params (example):

        scenario_prompt_key: "chart_scenarios_prompt"   # YAML prompt key
        num_scenarios: 8                                # optional

    The prompt template should produce a JSON array of objects like:

        {
          "name": "Homework Problems",
          "x_label": "Day of the Week",
          "x_values": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
          "y_label": "Number of problems solved",
          "title": "Homework Problems Solved During the Week"
        }
    """
    prompt_key = chart_params.get("scenario_prompt_key", "chart_scenarios_prompt")
    num_scenarios = chart_params.get("num_scenarios", 8)

    prompt_template = load_prompt(prompt_key)

    # If your prompt uses a placeholder like {{NUM_SCENARIOS}}, fill it:
    prompt = prompt_template.replace("{{NUM_SCENARIOS}}", str(num_scenarios))

    scenarios = llm.invoke_json(prompt)
    if not isinstance(scenarios, list):
        raise ValueError("LLM scenario prompt did not return a JSON list")

    return scenarios


def choose_chart_type(chart_params: dict) -> ChartType:
    """
    Choose a chart type, defaulting to line/bar/pie if not configured.
    """
    allowed_types = chart_params.get("chart_types", ["line", "bar", "pie"])
    chart_type_str = random.choice(allowed_types)
    return ChartType(chart_type_str)


def generate_random_series_data(
    num_series: int,
    num_points: int,
    y_min: int,
    y_max: int,
    smooth_for_line: bool = True,
) -> List[List[int]]:
    """
    Generate random, simple integer data for each series.
    """
    all_values: List[List[int]] = []

    for _ in range(num_series):
        base = [random.randint(y_min, y_max) for _ in range(num_points)]

        if smooth_for_line and num_points > 1:
            running = 0
            values = []
            for i, val in enumerate(base, start=1):
                running += val
                values.append(running // i)
        else:
            values = base

        all_values.append(values)

    return all_values

def build_chart_context(
    template_cfg: dict,
    meta_cfg: dict,
    llm: BaseLLM,
) -> Dict[str, List[ChartQuestionContext]]:
    
    """
        Parameters
        ----------
        template_cfg : dict
            Template-level configuration for chart context building.
            Expected keys include (non-exhaustive):

            * ``"num_charts"`` : int
            Number of chart contexts to create.
            * ``"chart_params"`` : dict
            Dictionary of chart-specific parameters used by
            :func:`generate_scenarios_from_llm`,
            :func:`choose_chart_type` and
            :func:`generate_random_series_data`. Common keys:

            - ``"chart_types"`` : list of str
            - ``"min_points"`` : int
            - ``"max_points"`` : int
            - ``"min_series"`` : int
            - ``"max_series"`` : int
            - ``"y_min"`` : int
            - ``"y_max"`` : int
            - ``"legend_mode"`` : {"auto", "always", "never"}

        meta_cfg : dict
            Question metadata configuration. Expected keys include:

            * ``"id_prefix"`` : str
            * ``"year"`` : str or int
            * ``"subject"`` : str
            * ``"category"`` : str
            * ``"question_name_prefix"`` : str
            * ``"expected_time_secs"`` : int

        llm : BaseLLM
            LLM wrapper used to generate chart scenarios via
            :func:`generate_scenarios_from_llm`.

        Returns
        -------
        dict of str to list of ChartQuestionContext
            A mapping with a single key, ``"charts"``, whose value is
            a list of :class:`ChartQuestionContext` instances. Each
            context bundles:

            * ``meta`` : :class:`QuestionMeta`
            * ``payload`` : :class:`ChartPayload`

        Raises
        ------
        ValueError
            If the LLM returns no chart scenarios.

        Notes
        -----
        * Scenarios are reused in a round-robin fashion if
        ``num_charts`` exceeds the number of scenarios returned
        by the LLM.
        * For pie charts, only a single series is generated and the
        legend is disabled.
        * When ``legend_mode == "auto"``, the legend is shown only
        if there is more than one data series.
        """


    num_charts: int = template_cfg["num_charts"]
    chart_params: dict = template_cfg["chart_params"]

    # 1) Ask the LLM for scenarios
    scenarios_from_llm = generate_scenarios_from_llm(llm, chart_params)
    # breakpoint()
    if not scenarios_from_llm:
        raise ValueError("LLM returned no chart scenarios")

    contexts: List[ChartQuestionContext] = []
    builder = ChartContextBuilder()

    # Defaults
    min_points: int = chart_params.get("min_points", 3)
    max_points: int = chart_params.get("max_points", 6)
    min_series: int = chart_params.get("min_series", 1)
    max_series: int = chart_params.get("max_series", 2)
    y_min: int = chart_params.get("y_min", 5)
    y_max: int = chart_params.get("y_max", 50)
    legend_mode = chart_params.get("legend_mode", "auto")  # "auto" | "always" | "never"

    for i in range(num_charts):
        # Scenario (round-robin)
        scenario = scenarios_from_llm[i % len(scenarios_from_llm)]
        chart_type = choose_chart_type(chart_params)

        full_x_values = scenario["x_values"]
        max_allowed_points = min(len(full_x_values), max_points)
        num_points = max(min_points, max_allowed_points)
        if num_points > len(full_x_values):
            num_points = len(full_x_values)

        # Sample indices but keep order
        chosen_indices = sorted(random.sample(range(len(full_x_values)), k=num_points))
        x_values = [full_x_values[idx] for idx in chosen_indices]

        if chart_type == ChartType.PIE:
            num_series = 1
        else:
            num_series = random.randint(min_series, max_series)

        series_names = [f"Class {chr(ord('A') + s)}" for s in range(num_series)]

        if chart_type == ChartType.PIE:
            show_legend = False
        else:    
            if legend_mode == "always":
                show_legend = True
            elif legend_mode == "never":
                show_legend = False
            else:  # auto
                show_legend = num_series > 1

        # Generate values
        smooth_for_line = chart_type.value == "line"
        values = generate_random_series_data(
            num_series=num_series,
            num_points=num_points,
            y_min=y_min,
            y_max=y_max,
            smooth_for_line=smooth_for_line,
        )

        # Build payload
        payload = builder.build(
            chart_type=chart_type,
            title=scenario["title"],
            x_label=scenario["x_label"],
            y_label=scenario["y_label"],
            x_values=x_values,
            series_names=series_names,
            values=values,
            show_legend=show_legend,
        )

        # Meta
        meta = QuestionMeta(
            id=f'{meta_cfg["id_prefix"]}{i + 1}',
            year=meta_cfg["year"],
            subject=meta_cfg["subject"],
            category=meta_cfg["category"],
            question_name=f'{meta_cfg["question_name_prefix"]}{i + 1}',
            expected_time_secs=meta_cfg["expected_time_secs"],
        )

        contexts.append(ChartQuestionContext(meta=meta, payload=payload))
        # breakpoint()
    return {"charts": contexts}
