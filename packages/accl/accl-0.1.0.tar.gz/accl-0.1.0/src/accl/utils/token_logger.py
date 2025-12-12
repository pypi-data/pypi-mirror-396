import json
import csv
import time
from pathlib import Path
from typing import Dict, List, Any


class TokenLogger:
    """
    Tracks detailed token usage across:
      - individual LLM calls
      - batches
      - templates
      - entire pipeline

    Provides export to JSON + CSV with timestamped filenames (no overwrite).
    """

    def __init__(self, run_id: str = "run"):
        self.start_time = time.time()
        self.run_id = run_id  # NEW
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")

        self.records: List[Dict[str, Any]] = []
        self.template_totals: Dict[str, Dict[str, int]] = {}
        self.pipeline_total_input = 0
        self.pipeline_total_output = 0

    def log_call(
        self,
        template_name: str,
        batch_id: int,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any],
    ):
        total = input_tokens + output_tokens

        self.records.append(
            {
                "template": template_name,
                "batch": batch_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total,
                "metadata": metadata,
            }
        )

        if template_name not in self.template_totals:
            self.template_totals[template_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
            }

        self.template_totals[template_name]["input_tokens"] += input_tokens
        self.template_totals[template_name]["output_tokens"] += output_tokens

        self.pipeline_total_input += input_tokens
        self.pipeline_total_output += output_tokens

    def export_json(self, directory: str = "reports"):
        Path(directory).mkdir(parents=True, exist_ok=True)
        filename = f"{directory}/token_usage_{self.timestamp}.json"

        data = {
            "pipeline_runtime_sec": time.time() - self.start_time,
            "pipeline_totals": {
                "input_tokens": self.pipeline_total_input,
                "output_tokens": self.pipeline_total_output,
                "total_tokens": self.pipeline_total_input + self.pipeline_total_output,
            },
            "per_template": self.template_totals,
            "records": self.records,
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        return filename

    def export_csv(self, directory: str = "reports"):
        Path(directory).mkdir(parents=True, exist_ok=True)
        filename = f"{directory}/token_usage_{self.timestamp}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["template", "batch", "input_tokens", "output_tokens", "total_tokens"])
            for r in self.records:
                writer.writerow([
                    r["template"],
                    r["batch"],
                    r["input_tokens"],
                    r["output_tokens"],
                    r["total_tokens"],
                ])

        return filename
