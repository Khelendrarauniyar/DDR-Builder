from src.fusion.conflict_detector import detect_conflicts
from src.models import EvidenceSpan, FindingClaim


def claim(cid: str, temp: str):
    return FindingClaim(
        claim_id=cid,
        area="kitchen",
        issue="thermal hotspot",
        observation_text="Heat anomaly in kitchen panel.",
        thermal_reading=temp,
        evidence_spans=[EvidenceSpan(doc_id="d1", page=1, char_start=0, char_end=10, text="x")],
        confidence=0.8,
    )


def test_detect_conflict():
    conflicts = detect_conflicts([claim("c1", "35.0°C"), claim("c2", "49.0°C")])
    assert len(conflicts) == 1
