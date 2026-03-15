from __future__ import annotations

from src.models import FindingClaim


ROOT_CAUSE_TABLE = {
    "moisture": "Possible waterproofing failure or persistent plumbing leak",
    "thermal hotspot": "Possible overloaded electrical component or poor ventilation",
    "insulation": "Likely insulation gap or thermal bridging",
    "crack": "Possible settlement or material fatigue",
    "mold": "Likely prolonged dampness and low ventilation",
}


def infer_root_cause(claims: list[FindingClaim]) -> list[FindingClaim]:
    for claim in claims:
        if claim.probable_root_cause:
            continue
        claim.probable_root_cause = ROOT_CAUSE_TABLE.get(claim.issue, "Not Available")
    return claims
