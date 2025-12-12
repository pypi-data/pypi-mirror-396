from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from accl.schemas.chart import ChartPayload, ChartType
from accl.render.base import BaseRenderer


def chart_payload_to_dataframe(payload: ChartPayload) -> pd.DataFrame:
    """
    Convert a ChartPayload into a tidy DataFrame.

    Columns:
      - x: category label (from x_values)
      - series: series name (from series_names)
      - y: numeric value
    """
    rows: list[dict[str, object]] = []

    x_values = payload.x_values
    series_names = payload.series_names
    values = payload.values

    for s_idx, series in enumerate(series_names):
        series_values = values[s_idx]
        for x, y in zip(x_values, series_values):
            rows.append({"x": x, "series": series, "y": y})
    return pd.DataFrame(rows)


class ChartRenderer(BaseRenderer[ChartPayload]):
    """
    Concrete renderer for ChartPayload.

    Usage:
        renderer = ChartRenderer()
        out_path = renderer.render(payload)
    """

    def __init__(self, dpi: int = 150) -> None:
        super().__init__(subdir="charts", dpi=dpi)

    def _render_core(self, payload: ChartPayload, out_path: Path) -> None:
        df = chart_payload_to_dataframe(payload)

        plt.figure(figsize=(8, 5))
        sns.set_theme(style="whitegrid")

        chart_type = payload.chart_type

        if chart_type == ChartType.LINE:
            sns.lineplot(data=df, x="x", y="y", hue="series", marker="o")
            plt.xlabel(payload.x_label)
            plt.ylabel(payload.y_label)

        elif chart_type == ChartType.BAR:
            sns.barplot(data=df, x="x", y="y", hue="series")
            plt.xlabel(payload.x_label)
            plt.ylabel(payload.y_label)

        elif chart_type == ChartType.PIE:
            # For pie charts we ignore series and assume a single series (or sum).
            if len(payload.series_names) == 1:
                pie_values = payload.values[0]
            else:
                sums = df.groupby("x")["y"].sum().reindex(payload.x_values)
                pie_values = sums.tolist()

            plt.pie(
                pie_values,
                labels=payload.x_values,
                autopct="%1.1f%%",
                startangle=90,
            )
            plt.ylabel("")

        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Legend handling
        if chart_type in (ChartType.LINE, ChartType.BAR):
            if payload.show_legend and len(payload.series_names) > 1:
                plt.legend(title="Series")
            else:
                leg = plt.gca().legend()
                if leg is not None:
                    leg.remove()

        plt.title(payload.title)
        plt.tight_layout()
        plt.savefig(out_path, dpi=self.dpi)
        plt.close()


def render_chart_payload(
    payload: ChartPayload,
    save_dir: Path | str | None = None,
    filename: str | None = None,
    dpi: int = 150,
) -> Path:
    renderer = ChartRenderer(dpi=dpi)
    return renderer.render(payload, save_dir=save_dir, filename=filename)

