from __future__ import annotations

from src.common.text_utils import normalize_text
from src.models import FindingClaim, SourceDocument


def align_evidence(claims: list[FindingClaim], documents: list[SourceDocument]) -> list[FindingClaim]:
    aligned: list[FindingClaim] = []
    doc_map = {d.doc_id: d for d in documents}

    for claim in claims:
        if not claim.evidence_spans:
            continue
        span = claim.evidence_spans[0]
        doc = doc_map.get(span.doc_id)
        if not doc:
            continue

        page_block = next((b for b in doc.text_blocks if b.page == span.page), None)
        if not page_block:
            continue

        snippet = normalize_text(span.text).lower()
        text = normalize_text(page_block.text).lower()
        if snippet and snippet in text:
            aligned.append(claim)

    return aligned
