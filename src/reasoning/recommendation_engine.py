from __future__ import annotations

from src.models import FindingClaim


RECOMMENDATION_TABLE = {
    "moisture": "Inspect waterproofing and plumbing in the area, then dry and repair affected surfaces.",
    "thermal hotspot": "Perform electrical and thermal safety inspection; reduce load and improve ventilation.",
    "insulation": "Add or repair insulation and seal thermal leakage points.",
    "crack": "Assess structural condition and seal or repair crack based on engineer advice.",
    "mold": "Remove mold safely, treat root moisture source, and improve ventilation.",
}


def generate_recommendations(claims: list[FindingClaim]) -> list[FindingClaim]:
    for claim in claims:
        if claim.recommendation:
            continue
        claim.recommendation = RECOMMENDATION_TABLE.get(claim.issue, "Not Available")
    return claims
