from __future__ import annotations

from pathlib import Path
import json

from src.common.logging_utils import StageTimer, configure_logging, log_event
from src.config import load_config
from src.extract.evidence_aligner import align_evidence
from src.extract.llm_extractor import parse_llm_claims
from src.extract.rule_parser import parse_rule_claims
from src.fusion.claim_merger import merge_claims
from src.fusion.conflict_detector import detect_conflicts
from src.ingest.document_loader import load_documents
from src.ingest.image_extractor import extract_images
from src.reasoning.recommendation_engine import generate_recommendations
from src.reasoning.root_cause_engine import infer_root_cause
from src.reasoning.severity_engine import assign_severity
from src.report.ddr_composer import compose_ddr, render_markdown
from src.validation.reliability_gates import run_gates
from src.validation.schema_validator import validate_ddr_schema


def run_pipeline(inspection_path: str, thermal_path: str, output_dir: str, config_path: str | None = None) -> int:
    configure_logging()
    cfg = load_config(config_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        with StageTimer("ingestion"):
            documents = load_documents(inspection_path, thermal_path)

        with StageTimer("image_extraction"):
            images = extract_images(documents, output_dir)

        with StageTimer("claim_extraction"):
            rule_claims = parse_rule_claims(documents)
            llm_claims = parse_llm_claims(
                documents,
                model=cfg.llm_model,
                enabled=cfg.llm_enabled,
                provider=cfg.llm_provider,
                api_base_url=cfg.groq_base_url,
                timeout_seconds=cfg.llm_timeout_seconds,
            )
            claims = rule_claims + llm_claims

        with StageTimer("evidence_alignment"):
            claims = align_evidence(claims, documents)

        with StageTimer("fusion"):
            merged = merge_claims(claims, similarity_threshold=cfg.similarity_threshold)
            conflicts = detect_conflicts(merged)

        with StageTimer("reasoning"):
            merged = assign_severity(merged, cfg.medium_temp_threshold_c, cfg.high_temp_threshold_c)
            merged = infer_root_cause(merged)
            merged = generate_recommendations(merged)

        with StageTimer("compose_report"):
            ddr = compose_ddr(merged, conflicts, images)

        with StageTimer("validation"):
            run_gates(ddr, merged, conflicts)
            validate_ddr_schema(ddr)

        with StageTimer("persist"):
            _persist_outputs(out_dir, ddr, merged, conflicts, images)

        log_event("pipeline", "success", output_dir=str(out_dir))
        return 0
    except Exception as exc:
        log_event("pipeline", "failure", error=str(exc))
        return 1


def _persist_outputs(out_dir: Path, ddr, claims, conflicts, images) -> None:
    markdown = render_markdown(ddr)
    (out_dir / "ddr_report.md").write_text(markdown, encoding="utf-8")

    payload = {
        "ddr": ddr.model_dump(),
        "claims": [c.model_dump() for c in claims],
        "conflicts": [c.model_dump() for c in conflicts],
        "images": [i.model_dump() for i in images],
    }
    (out_dir / "artifacts.json").write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
