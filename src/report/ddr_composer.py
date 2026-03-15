from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from src.models import AreaObservation, ConflictRecord, DdrReport, FindingClaim, ImageAsset


def compose_ddr(claims: list[FindingClaim], conflicts: list[ConflictRecord], images: list[ImageAsset]) -> DdrReport:
    by_area: dict[str, list[FindingClaim]] = defaultdict(list)
    for claim in claims:
        by_area[claim.area].append(claim)

    image_ref_by_page = {(img.doc_id, img.page): f"images/{Path(img.file_path).name}" for img in images}

    area_sections: list[AreaObservation] = []
    for area in sorted(by_area.keys()):
        items = by_area[area]
        observation = " ".join(f"- {c.observation_text}" for c in items)
        thermal_points = [c.thermal_reading for c in items if c.thermal_reading]
        thermal_data = ", ".join(thermal_points) if thermal_points else "Not Available"

        area_images: list[str] = []
        for claim in items:
            for span in claim.evidence_spans:
                key = (span.doc_id, span.page)
                if key in image_ref_by_page:
                    area_images.append(image_ref_by_page[key])

        area_images = list(dict.fromkeys(area_images))
        if not area_images:
            area_images = ["Image Not Available"]

        area_sections.append(
            AreaObservation(
                area=area,
                observation=observation if observation else "Not Available",
                thermal_data=thermal_data,
                images=area_images,
            )
        )

    summary = _build_summary(claims)
    root_cause = _build_root_cause(claims)
    severity = _build_severity(claims)
    recommendations = _build_recommendations(claims)
    notes = _build_notes(conflicts)
    missing = _build_missing(claims, images)

    return DdrReport(
        property_issue_summary=summary,
        area_wise_observations=area_sections,
        probable_root_cause=root_cause,
        severity_assessment=severity,
        recommended_actions=recommendations,
        additional_notes=notes,
        missing_or_unclear_information=missing,
    )


def render_markdown(ddr: DdrReport) -> str:
    lines: list[str] = []
    lines.append("# Detailed Diagnostic Report (DDR)")
    lines.append("")
    lines.append("## 1. Property Issue Summary")
    lines.append(ddr.property_issue_summary)
    lines.append("")
    lines.append("## 2. Area-wise Observations")
    for area in ddr.area_wise_observations:
        lines.append(f"### {area.area.title()}")
        lines.append(f"Observation: {area.observation}")
        lines.append(f"Thermal Data: {area.thermal_data}")
        lines.append("Images:")
        for image in area.images:
            if image == "Image Not Available":
                lines.append("- Image Not Available")
            else:
                lines.append(f"- ![{area.area} evidence]({image})")
        lines.append("")
    lines.append("## 3. Probable Root Cause")
    lines.append(ddr.probable_root_cause)
    lines.append("")
    lines.append("## 4. Severity Assessment")
    lines.append(ddr.severity_assessment)
    lines.append("")
    lines.append("## 5. Recommended Actions")
    lines.append(ddr.recommended_actions)
    lines.append("")
    lines.append("## 6. Additional Notes")
    lines.append(ddr.additional_notes)
    lines.append("")
    lines.append("## 7. Missing or Unclear Information")
    lines.append(ddr.missing_or_unclear_information)
    lines.append("")
    return "\n".join(lines)


def _build_summary(claims: list[FindingClaim]) -> str:
    if not claims:
        return "Not Available"
    issue_counts: dict[str, int] = defaultdict(int)
    for c in claims:
        issue_counts[c.issue] += 1
    parts = [f"{issue}: {count}" for issue, count in sorted(issue_counts.items(), key=lambda x: (-x[1], x[0]))]
    return "Detected issues by frequency: " + "; ".join(parts)


def _build_root_cause(claims: list[FindingClaim]) -> str:
    causes = [c.probable_root_cause for c in claims if c.probable_root_cause and c.probable_root_cause != "Not Available"]
    if not causes:
        return "Not Available"
    return "; ".join(sorted(set(causes)))


def _build_severity(claims: list[FindingClaim]) -> str:
    if not claims:
        return "Not Available"
    order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    top = sorted((c.severity_label or "Low" for c in claims), key=lambda s: order.get(s, 0), reverse=True)[0]
    return f"Overall severity is {top}, based on issue patterns and thermal/safety indicators."


def _build_recommendations(claims: list[FindingClaim]) -> str:
    recs = [c.recommendation for c in claims if c.recommendation and c.recommendation != "Not Available"]
    if not recs:
        return "Not Available"
    return " ".join(f"- {r}" for r in sorted(set(recs)))


def _build_notes(conflicts: list[ConflictRecord]) -> str:
    if not conflicts:
        return "No direct conflicts detected between the two source documents."
    lines = []
    for c in conflicts:
        lines.append(
            f"Conflict in {c.area} for {c.field_name}: '{c.value_a}' vs '{c.value_b}'. {c.resolution_note}"
        )
    return " ".join(lines)


def _build_missing(claims: list[FindingClaim], images: list[ImageAsset]) -> str:
    if not claims:
        return "Not Available: No extractable findings were identified from source documents. Image Not Available"

    missing: list[str] = []
    if not images:
        missing.append("Image Not Available")

    areas_missing_thermal = sorted({c.area for c in claims if not c.thermal_reading})
    if areas_missing_thermal:
        missing.append(f"Not Available thermal readings for: {', '.join(areas_missing_thermal)}")

    areas_missing_root = sorted({c.area for c in claims if not c.probable_root_cause or c.probable_root_cause == 'Not Available'})
    if areas_missing_root:
        missing.append(f"Not Available probable root cause for: {', '.join(areas_missing_root)}")

    areas_missing_reco = sorted({c.area for c in claims if not c.recommendation or c.recommendation == 'Not Available'})
    if areas_missing_reco:
        missing.append(f"Not Available recommendations for: {', '.join(areas_missing_reco)}")

    return " ".join(missing) if missing else "No significant missing information identified."
