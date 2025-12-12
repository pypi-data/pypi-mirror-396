from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from accl.render.base import BaseRenderer
from accl.schemas.angle import AnglePayload


class AngleRenderer(BaseRenderer[AnglePayload]):
    def __init__(self, dpi: int = 150) -> None:
        super().__init__(
            subdir="angles",
            dpi=dpi,
        )

    @staticmethod
    def _unique_path(save_dir: Path, base_name: str) -> Path:
        save_dir.mkdir(parents=True, exist_ok=True)
        candidate = save_dir / base_name
        if not candidate.exists():
            return candidate
        stem, suffix = candidate.stem, candidate.suffix
        i = 1
        while True:
            new_path = save_dir / f"{stem}_{i}{suffix}"
            if not new_path.exists():
                return new_path
            i += 1

    def _build_output_path(self, payload: AnglePayload, save_dir, filename):
        save_dir = Path(save_dir) if save_dir else self.render_root / self.subdir
        if filename is None:
            filename = f"{self._slugify(f'angle_{payload.angle_degrees}_deg')}.png"
        return self._unique_path(save_dir, filename)

    def _render_core(self, payload: AnglePayload, out_path: Path) -> None:
        angle = payload.angle_degrees
        theta = np.radians(angle)

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
        ax.set_theta_direction(-1)
        ax.set_theta_offset(np.pi / 2)
        ax.set_axis_off()

        if payload.show_inner_arc:
            ax.plot(np.linspace(0, theta, 200), [0.5] * 200, linewidth=6)
        if payload.show_outer_arc:
            ax.plot(np.linspace(0, theta, 200), [1.0] * 200, linewidth=6)

        ax.plot([0, 0], [0, 1], color="black", linewidth=2)
        ax.plot([0, theta], [0, 1], color="black", linewidth=2)

        if payload.show_inner_value:
            ax.text(theta / 2, 0.35, f"{angle}°", fontsize=14, ha="center")
        if payload.show_outer_value:
            ax.text(theta / 2, 1.15, f"{angle}°", fontsize=14, ha="center")

        ax.set_rlim(0, 1.2)
        ax.set_title(f"{angle}°", fontsize=16, pad=20)

        plt.tight_layout()
        plt.savefig(out_path, dpi=self.dpi)
        plt.close(fig)


def render_angle_payload(payload, save_dir=None, filename=None, dpi=150):
    return AngleRenderer(dpi=dpi).render(payload, save_dir, filename)
