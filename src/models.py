from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal


class TextBlock(BaseModel):
    page: int
    text: str


class EvidenceSpan(BaseModel):
    doc_id: str
    page: int
    char_start: int
    char_end: int
    text: str


class ImageAsset(BaseModel):
    image_id: str
    doc_id: str
    page: int
    file_path: str
    hash_sha256: str
    caption_guess: str | None = None


class SourceDocument(BaseModel):
    doc_id: str
    doc_type: Literal["inspection", "thermal"]
    file_path: str
    text_blocks: list[TextBlock] = Field(default_factory=list)


class FindingClaim(BaseModel):
    claim_id: str
    area: str
    issue: str
    observation_text: str
    thermal_reading: str | None = None
    probable_root_cause: str | None = None
    severity_label: str | None = None
    recommendation: str | None = None
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    image_refs: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class ConflictRecord(BaseModel):
    area: str
    field_name: str
    value_a: str
    value_b: str
    evidence_a: list[EvidenceSpan]
    evidence_b: list[EvidenceSpan]
    resolution_note: str


class AreaObservation(BaseModel):
    area: str
    observation: str
    thermal_data: str
    images: list[str] = Field(default_factory=list)


class DdrReport(BaseModel):
    property_issue_summary: str
    area_wise_observations: list[AreaObservation]
    probable_root_cause: str
    severity_assessment: str
    recommended_actions: str
    additional_notes: str
    missing_or_unclear_information: str
