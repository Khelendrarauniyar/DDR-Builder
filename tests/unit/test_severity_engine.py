from src.reasoning.severity_engine import assign_severity
from src.models import EvidenceSpan, FindingClaim


def test_assign_severity_high_temp():
    claims = [
        FindingClaim(
            claim_id="c1",
            area="kitchen",
            issue="thermal hotspot",
            observation_text="Electrical hazard with hotspot near panel.",
            thermal_reading="48.0°C",
            evidence_spans=[EvidenceSpan(doc_id="d1", page=1, char_start=0, char_end=10, text="x")],
            confidence=0.8,
        )
    ]
    out = assign_severity(claims)
    assert out[0].severity_label in {"High", "Critical"}
