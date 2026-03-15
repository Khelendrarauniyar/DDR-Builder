from __future__ import annotations

import itertools
import re

from src.common.text_utils import extract_temperatures, normalize_area
from src.models import EvidenceSpan, FindingClaim, SourceDocument


ISSUE_KEYWORDS = {
    "moisture": ["moisture", "damp", "leak", "seepage", "water ingress", "wet"],
    "thermal hotspot": ["hotspot", "overheat", "high temperature", "thermal anomaly", "heat"],
    "insulation": ["insulation", "cold bridge", "heat loss"],
    "crack": ["crack", "fracture", "split"],
    "mold": ["mold", "mildew", "fungus"],
}

AREA_PATTERNS = [
    "kitchen", "living room", "hallway", "bathroom", "bedroom", "roof", "ceiling", "wall", "balcony", "staircase",
]


def parse_rule_claims(documents: list[SourceDocument]) -> list[FindingClaim]:
    claims: list[FindingClaim] = []
    claim_counter = itertools.count(1)

    for doc in documents:
        for block in doc.text_blocks:
            sentences = _split_sentences(block.text)
            for sentence in sentences:
                sentence_lower = sentence.lower()
                issue = _detect_issue(sentence_lower)
                if not issue:
                    continue

                area = _detect_area(sentence_lower)
                temps = extract_temperatures(sentence)
                thermal = f"{max(temps):.1f}°C" if temps else None

                span_start = max(0, block.text.lower().find(sentence_lower[:32]))
                span_end = span_start + len(sentence)
                claim_id = f"C{next(claim_counter):04d}"

                claims.append(
                    FindingClaim(
                        claim_id=claim_id,
                        area=normalize_area(area),
                        issue=issue,
                        observation_text=sentence.strip(),
                        thermal_reading=thermal,
                        evidence_spans=[
                            EvidenceSpan(
                                doc_id=doc.doc_id,
                                page=block.page,
                                char_start=span_start,
                                char_end=span_end,
                                text=sentence.strip(),
                            )
                        ],
                        confidence=0.65,
                    )
                )

    return claims


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]


def _detect_issue(sentence: str) -> str | None:
    for issue, keywords in ISSUE_KEYWORDS.items():
        if any(k in sentence for k in keywords):
            return issue
    return None


def _detect_area(sentence: str) -> str:
    for area in AREA_PATTERNS:
        if area in sentence:
            return area

    if " in " in sentence:
        candidate = sentence.split(" in ", maxsplit=1)[-1].split(" ", maxsplit=2)[:2]
        return " ".join(candidate)

    return "general"
