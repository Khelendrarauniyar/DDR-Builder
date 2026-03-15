from __future__ import annotations

from src.common.text_utils import extract_temperatures
from src.models import FindingClaim


def assign_severity(claims: list[FindingClaim], medium_temp_threshold_c: float = 35.0, high_temp_threshold_c: float = 45.0) -> list[FindingClaim]:
    for claim in claims:
        score = 0
        text = claim.observation_text.lower()
        temps = extract_temperatures(claim.thermal_reading or "")
        max_temp = max(temps) if temps else None

        if any(k in text for k in ["fire", "electrical", "hazard", "structural"]):
            score += 3
        if any(k in text for k in ["leak", "moisture", "mold", "seepage"]):
            score += 2
        if max_temp is not None and max_temp >= high_temp_threshold_c:
            score += 3
        elif max_temp is not None and max_temp >= medium_temp_threshold_c:
            score += 2

        claim.severity_label = _label_from_score(score)

    return claims


def _label_from_score(score: int) -> str:
    if score >= 6:
        return "Critical"
    if score >= 4:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"
