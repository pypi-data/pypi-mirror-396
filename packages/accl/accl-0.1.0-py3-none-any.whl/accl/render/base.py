from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Optional, TypeVar

PayloadT = TypeVar("PayloadT")


def _default_render_root() -> Path:
    """
    Determine the base directory for all renders.

    Priority:
    1. RENDERS_DIR environment variable (if set).
    2. ``Path.cwd() / "renders"``

    This means:
    - In Docker, WORKDIR=/app → /app/renders (mounted to ./renders on host)
    - In local dev, if you run from the project root → ./renders
    """
    env_dir = os.getenv("RENDERS_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd() / "renders"


class BaseRenderer(ABC, Generic[PayloadT]):
    """
    Base class for anything that turns a payload into a rendered artefact on disk
    (usually a PNG).

    Subclasses only implement `_render_core` – all the path/slug/dpi stuff lives here.

    Parameters
    ----------
    subdir : str
        Subdirectory under the render root where this renderer will write files
        (for example, ``"datatables"`` or ``"charts"``).
    dpi : int, optional
        DPI used when saving matplotlib figures.
    render_root : Path, optional
        Explicit base directory for all renders. If omitted, this defaults to
        `_default_render_root()`.
    """

    def __init__(
        self,
        subdir: str,
        dpi: int = 150,
        render_root: Path | None = None,
    ) -> None:
        import matplotlib
        matplotlib.use("Agg")

        # Root dir where all renders live (e.g. ./renders or /app/renders)
        if render_root is None:
            render_root = _default_render_root()

        self.render_root = render_root
        self.subdir = subdir
        self.dpi = dpi

    # ---------- public API ----------

    def render(
        self,
        payload: PayloadT,
        save_dir: Path | str | None = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Orchestrate rendering:
        - decide directory
        - build filename (slugified from payload if needed)
        - create dirs
        - delegate to `_render_core`
        """
        out_path = self._build_output_path(payload, save_dir, filename)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        self._render_core(payload, out_path)

        return out_path

    # ---------- hooks for subclasses ----------

    @abstractmethod
    def _render_core(self, payload: PayloadT, out_path: Path) -> None:
        """
        Do the actual drawing/writing and save to `out_path`.

        Subclasses must call whatever plotting / PIL / etc they need and save to
        `out_path`. DPI is available as `self.dpi` if using matplotlib.
        """
        raise NotImplementedError

    # ---------- helpers ----------

    def _build_output_path(
        self,
        payload: PayloadT,
        save_dir: Path | str | None,
        filename: Optional[str],
    ) -> Path:
        if save_dir is None:
            save_dir = self.render_root / self.subdir
        else:
            save_dir = Path(save_dir)

        if filename is None:
            base = self._infer_basename_from_payload(payload)
            filename = f"{self._slugify(base)}.png"

        return save_dir / filename

    def _infer_basename_from_payload(self, payload: PayloadT) -> str:
        # Try a few common attributes; fall back to the class name
        for attr in ("title", "name", "code", "id"):
            if hasattr(payload, attr):
                value = getattr(payload, attr)
                if isinstance(value, str) and value.strip():
                    return value
        return self.__class__.__name__.replace("Renderer", "").lower()

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text)
        return text.strip("_") or "render"
