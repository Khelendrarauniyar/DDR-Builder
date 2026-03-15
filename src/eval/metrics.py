from __future__ import annotations

from src.models import ConflictRecord, DdrReport, FindingClaim


def compute_metrics(ddr: DdrReport, claims: list[FindingClaim], conflicts: list[ConflictRecord]) -> dict[str, float]:
    if not claims:
        return {
            "faithfulness": 0.0,
            "completeness": 0.0,
            "conflict_transparency": 1.0 if not conflicts else 0.0,
            "claim_count": 0.0,
        }

    evidence_backed = sum(1 for c in claims if c.evidence_spans)
    faithfulness = evidence_backed / len(claims)

    required_present = all(
        [
            bool(ddr.property_issue_summary.strip()),
            bool(ddr.area_wise_observations),
            bool(ddr.probable_root_cause.strip()),
            bool(ddr.severity_assessment.strip()),
            bool(ddr.recommended_actions.strip()),
            bool(ddr.additional_notes.strip()),
            bool(ddr.missing_or_unclear_information.strip()),
        ]
    )
    completeness = 1.0 if required_present else 0.0

    if conflicts:
        conflict_transparency = 1.0 if "Conflict" in ddr.additional_notes else 0.0
    else:
        conflict_transparency = 1.0

    return {
        "faithfulness": round(faithfulness, 3),
        "completeness": completeness,
        "conflict_transparency": conflict_transparency,
        "claim_count": float(len(claims)),
    }
