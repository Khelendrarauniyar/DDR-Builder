from __future__ import annotations

import json
import logging
import time


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_event(stage: str, message: str, **kwargs: object) -> None:
    payload = {"stage": stage, "message": message, **kwargs}
    logging.info(json.dumps(payload, ensure_ascii=True))


class StageTimer:
    def __init__(self, stage: str):
        self.stage = stage
        self.started_at = 0.0

    def __enter__(self) -> "StageTimer":
        self.started_at = time.perf_counter()
        log_event(self.stage, "started")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        duration_ms = int((time.perf_counter() - self.started_at) * 1000)
        if exc is None:
            log_event(self.stage, "completed", duration_ms=duration_ms)
        else:
            log_event(self.stage, "failed", duration_ms=duration_ms, error=str(exc))
