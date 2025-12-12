from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from typing import Optional
from accl.render.base import BaseRenderer
from accl.schemas.datatable import DataTablePayload


class DataTableRenderer(BaseRenderer[DataTablePayload]):
    """
    Concrete renderer for DataTablePayload.

    Default output directory:
        <render_root>/datatables

    where ``render_root`` is either:
      - the value of the RENDERS_DIR environment variable, or
      - ``Path.cwd() / "renders"``.
    """

    def __init__(self, dpi: int = 150) -> None:
        super().__init__(
            subdir="datatables",
            dpi=dpi,
        )

    # Optionally override to keep your old "use header row as filename" logic
    def _infer_basename_from_payload(self, payload: DataTablePayload) -> str:
        if payload.header_first_row and payload.cells:
            header_row = payload.cells[0]
            header_text = " ".join(header_row)
            if header_text.strip():
                return header_text
        # Fall back to the generic logic (title/name/code/id or class name)
        return super()._infer_basename_from_payload(payload)

    def _render_core(self, payload: DataTablePayload, out_path: Path) -> None:
        cells = payload.cells
        n_rows = len(cells)
        n_cols = len(cells[0]) if cells else 0

        width = max(4, n_cols * 1.2)
        height = max(2, n_rows * 0.6)

        fig, ax = plt.subplots(figsize=(width, height))
        ax.axis("off")

        # Draw the table
        table = ax.table(
            cellText=cells,
            loc="center",
            cellLoc="center",
        )

        # Make it a bit more readable
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.0, 1.2)

        # Style header row and/or header column
        header_color = "#e0f0ff"
        header_fontweight = "bold"

        for (row, col), cell in table.get_celld().items():
            if row < 0 or col < 0:
                continue

            if payload.header_first_row and row == 0:
                cell.set_facecolor(header_color)
                cell.get_text().set_fontweight(header_fontweight)

            if payload.header_first_col and col == 0:
                cell.set_facecolor(header_color)
                cell.get_text().set_fontweight(header_fontweight)

        plt.tight_layout()
        plt.savefig(out_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)


def render_datatable_payload(
    payload: DataTablePayload,
    save_dir: Path | str | None = None,
    filename: Optional[str] = None,
    dpi: int = 150,
) -> Path:
    return DataTableRenderer(dpi=dpi).render(
        payload,
        save_dir=save_dir,
        filename=filename,
    )
