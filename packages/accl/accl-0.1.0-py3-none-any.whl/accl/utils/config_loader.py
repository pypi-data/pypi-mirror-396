from pathlib import Path
import logging
import yaml
from typing import Any, Dict

# /usr/local/lib/python3.12/site-packages/accl/utils/config_loader.py
# parent of this file is .../accl/utils
# parent.parent is .../accl  -> where configs/ lives now
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PACKAGE_ROOT / "configs"


def load_template_config(file_path: str | None = None) -> Dict[str, Any]:
    path = Path(file_path) if file_path is not None else CONFIG_DIR / "template_config.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Template config YAML not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if "templates" not in data or "question_meta_configs" not in data:
        raise KeyError(
            "template_config.yaml must contain 'templates' and 'question_meta_configs' mappings."
        )

    return data


def load_model_config(file_path: str | None = None) -> Dict[str, Any]:
    path = Path(file_path) if file_path is not None else CONFIG_DIR / "model_config.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Model config YAML not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return data


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
