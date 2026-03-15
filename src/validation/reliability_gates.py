from __future__ import annotations

from src.models import ConflictRecord, DdrReport, FindingClaim


def run_gates(ddr: DdrReport, claims: list[FindingClaim], conflicts: list[ConflictRecord]) -> None:
    _required_sections_gate(ddr)
    _missing_policy_gate(ddr)
    _conflict_visibility_gate(ddr, conflicts)
    _evidence_gate(claims)


def _required_sections_gate(ddr: DdrReport) -> None:
    required_values = [
        ddr.property_issue_summary,
        ddr.probable_root_cause,
        ddr.severity_assessment,
        ddr.recommended_actions,
        ddr.additional_notes,
        ddr.missing_or_unclear_information,
    ]
    if any(v is None or str(v).strip() == "" for v in required_values):
        raise ValueError("Required DDR section is empty")



def _missing_policy_gate(ddr: DdrReport) -> None:
    if not ddr.area_wise_observations:
        raise ValueError("Area-wise observations cannot be empty")
    for area in ddr.area_wise_observations:
        if not area.images:
            raise ValueError("Area observation missing image placeholder")



def _conflict_visibility_gate(ddr: DdrReport, conflicts: list[ConflictRecord]) -> None:
    if conflicts and "Conflict" not in ddr.additional_notes:
        raise ValueError("Conflicts exist but are not surfaced in Additional Notes")



def _evidence_gate(claims: list[FindingClaim]) -> None:
    for claim in claims:
        if not claim.evidence_spans:
            raise ValueError(f"Claim {claim.claim_id} has no evidence span")
