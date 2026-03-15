from __future__ import annotations

from src.models import DdrReport


def validate_ddr_schema(ddr: DdrReport) -> None:
    # Pydantic model already enforces schema; this call exists for explicit stage wiring.
    DdrReport.model_validate(ddr.model_dump())
