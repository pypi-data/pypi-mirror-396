import yaml
import os
from pathlib import Path
from typing import Dict, Any

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PACKAGE_ROOT / "configs"


def load_prompt(template_name: str, file_path: str | None = None) -> Dict[str, Any]:
    file_path = Path(file_path) if file_path is not None else CONFIG_DIR / "prompt_templates.yaml"

    """
    Load a specific prompt from a YAML file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt template YAML not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if template_name not in data:
        raise KeyError(f"Template '{template_name}' not found in YAML file.")

    return data[template_name]
