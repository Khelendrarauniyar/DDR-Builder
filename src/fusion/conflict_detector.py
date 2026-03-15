from __future__ import annotations

from collections import defaultdict

from src.models import ConflictRecord, FindingClaim


def detect_conflicts(claims: list[FindingClaim]) -> list[ConflictRecord]:
    grouped: dict[tuple[str, str], list[FindingClaim]] = defaultdict(list)
    for claim in claims:
        grouped[(claim.area, claim.issue)].append(claim)

    conflicts: list[ConflictRecord] = []
    for (area, issue), items in grouped.items():
        conflicts.extend(_find_field_conflicts(area, issue, items, "thermal_reading"))
        conflicts.extend(_find_field_conflicts(area, issue, items, "probable_root_cause"))
        conflicts.extend(_find_field_conflicts(area, issue, items, "severity_label"))
        conflicts.extend(_find_field_conflicts(area, issue, items, "recommendation"))

    return conflicts


def _find_field_conflicts(area: str, issue: str, items: list[FindingClaim], field_name: str) -> list[ConflictRecord]:
    field_values: list[str] = []
    for item in items:
        value = getattr(item, field_name, None)
        if not value or str(value).strip() == "" or value == "Not Available":
            continue
        field_values.append(value)

    unique_values = sorted(set(field_values))
    if len(unique_values) <= 1:
        return []

    first = unique_values[0]
    second = unique_values[1]
    claim_a = next(c for c in items if getattr(c, field_name, None) == first)
    claim_b = next(c for c in items if getattr(c, field_name, None) == second)

    return [
        ConflictRecord(
            area=area,
            field_name=f"{issue}.{field_name}",
            value_a=first,
            value_b=second,
            evidence_a=claim_a.evidence_spans,
            evidence_b=claim_b.evidence_spans,
            resolution_note="Conflict detected from multiple source statements. Manual verification advised.",
        )
    ]
