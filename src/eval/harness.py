from __future__ import annotations

from pathlib import Path
import json

from src.eval.metrics import compute_metrics


def evaluate_from_artifacts(artifact_json_path: str, output_path: str) -> None:
    source = Path(artifact_json_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    ddr = payload["ddr"]
    claims = payload["claims"]
    conflicts = payload["conflicts"]

    class Obj:
        def __init__(self, data: dict):
            self.__dict__.update(data)

    metric_values = compute_metrics(Obj(ddr), [Obj(c) for c in claims], [Obj(c) for c in conflicts])
    Path(output_path).write_text(json.dumps(metric_values, ensure_ascii=True, indent=2), encoding="utf-8")
