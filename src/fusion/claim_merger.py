from __future__ import annotations

from collections import defaultdict
from rapidfuzz import fuzz

from src.common.text_utils import normalize_area, normalize_text
from src.models import FindingClaim


def merge_claims(claims: list[FindingClaim], similarity_threshold: float = 0.84) -> list[FindingClaim]:
    grouped: dict[str, list[FindingClaim]] = defaultdict(list)
    for claim in claims:
        key = normalize_area(claim.area)
        grouped[key].append(claim)

    merged: list[FindingClaim] = []
    for area, area_claims in grouped.items():
        bucket: list[FindingClaim] = []
        for claim in area_claims:
            existing = _find_duplicate(claim, bucket, similarity_threshold)
            if existing is None:
                bucket.append(claim)
                continue

            existing.evidence_spans.extend(claim.evidence_spans)
            existing.image_refs = list(dict.fromkeys(existing.image_refs + claim.image_refs))
            if claim.thermal_reading and not existing.thermal_reading:
                existing.thermal_reading = claim.thermal_reading
            existing.confidence = max(existing.confidence, claim.confidence)
            existing.observation_text = _pick_richer_text(existing.observation_text, claim.observation_text)

        merged.extend(bucket)

    return merged


def _find_duplicate(claim: FindingClaim, candidates: list[FindingClaim], threshold: float) -> FindingClaim | None:
    query = f"{normalize_text(claim.issue)} {normalize_text(claim.observation_text)}"
    for candidate in candidates:
        ref = f"{normalize_text(candidate.issue)} {normalize_text(candidate.observation_text)}"
        score = fuzz.token_set_ratio(query, ref) / 100.0
        if score >= threshold:
            return candidate
    return None


def _pick_richer_text(a: str, b: str) -> str:
    return a if len(a) >= len(b) else b
