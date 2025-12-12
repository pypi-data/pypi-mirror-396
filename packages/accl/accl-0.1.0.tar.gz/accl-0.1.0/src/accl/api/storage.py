# src/utils/storage.py

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


# Root directory for all temporary/generated artifacts.
# In Docker you can mount this as a volume.
def get_shared_root() -> Path:
    root = os.getenv("ACCL_SHARED_TEMP_DIR", "shared_temp")
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_outputs_dir() -> Path:
    root = get_shared_root()
    out_dir = root / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def get_reports_dir() -> Path:
    root = get_shared_root()
    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def save_run_json(run_id: str, data: Dict[str, Any]) -> Path:
    """
    Save a single run's result as JSON.

    `data` should already be a plain dict (e.g. result.model_dump()).

    Filename format:
        YYYYMMDD_HHMMSS__<run_id>.json
    """
    outputs_dir = get_outputs_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}__{run_id}.json"
    path = outputs_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return path
