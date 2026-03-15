# AI Generalist Assignment Submission

## Project Title
Applied AI Builder: DDR (Detailed Diagnostic Report) Generation from Inspection + Thermal Documents

## Objective
Build a reliable AI workflow that reads two technical inputs:

1. Inspection Report
2. Thermal Report

And generates a client-ready DDR that is structured, traceable, and robust to missing or conflicting information.

## Assignment Requirement Coverage
This implementation addresses each required output section:

1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

It also handles image extraction and placement under relevant observations, with explicit fallback text:

1. Not Available
2. Image Not Available

## System Design
The solution is implemented as a modular pipeline:

1. Ingestion
2. Extraction
3. Fusion
4. Reasoning
5. Report Composition
6. Validation

### Pipeline Stages
1. Ingestion
Reads PDF/DOCX files and extracts page-level text blocks and embedded images.

2. Extraction
Creates structured finding claims using rule-based parsing, plus optional Groq-powered extraction.

3. Fusion
Merges duplicate findings across documents and detects conflicting values.

4. Reasoning
Assigns severity, probable root causes, and recommendations.

5. Report Composition
Builds the final DDR in required section order and inserts section-relevant image references.

6. Validation Gates
Enforces required section completeness, conflict visibility, image placeholder policy, and evidence presence.

## Reliability and Safety Logic
To reduce hallucinations and improve trustworthiness, the workflow includes:

1. Evidence spans on extracted claims.
2. Explicit conflict records when values disagree.
3. Deterministic fallback if LLM provider is unavailable.
4. Required placeholders for missing text/image data.

## Tech Stack
1. Python 3.10+
2. Streamlit (demo UI)
3. Pydantic (typed data contracts)
4. PyMuPDF + python-docx (document parsing)
5. RapidFuzz (dedupe similarity)
6. Optional Groq API (OpenAI-compatible endpoint)

## Repository Structure
1. src/ingest: document and image extraction
2. src/extract: rule-based + optional LLM claim extraction
3. src/fusion: merge and conflict detection
4. src/reasoning: severity, root cause, recommendations
5. src/report: DDR assembly and markdown rendering
6. src/validation: reliability gates and schema checks
7. ui: Streamlit application
8. prompts: LLM prompt templates

## Setup and Run
### 1) Install dependencies
```powershell
& "e:/Ai-Generalist Assignment/.venv/Scripts/python.exe" -m pip install -r requirements.txt
```

### 2) Configure environment (optional Groq)
1. Copy .env.example to .env
2. Set GROQ_API_KEY in .env
3. Keep llm_enabled true in config.yaml to use Groq

### 3) Run backend pipeline
```powershell
& ".venv/Scripts/python.exe" -m src.main --inspection data/input/inspection.docx --thermal data/input/thermal.docx --output_dir data/output --config config.yaml
```

### 4) Run demo UI
```powershell
& ".venv/Scripts/python.exe" -m streamlit run ui/app.py
```

Open http://localhost:8501

## Output Artifacts
Primary generated files:

1. data/output/ddr_report.md
2. data/output/artifacts.json
3. data/output/images/*

## Testing
Run:

```powershell
& ".venv/Scripts/python.exe" -m pytest -q
```

## Submission Notes
This repository includes:

1. End-to-end runnable codebase
2. Interactive UI for demonstration
3. Structured output artifacts
4. Clear pipeline logs and deterministic fallback behavior when Groq API is unavailable

## Final Submission Checklist
Before submitting to the evaluator, prepare these external items:

1. GitHub repository link
2. Loom video link (3-5 minutes):
	- What you built
	- How it works
	- Limitations
	- Improvements planned
3. Optional live/demo link (if hosted)
4. One Google Drive folder named with your full name containing:
	- README and project source
	- Key output artifacts/screenshots
	- Any supplementary notes
5. Share only one Google Drive folder link

## Limitations
1. OCR fallback for scanned image-only PDFs is not yet implemented.
2. Image-to-observation mapping is page-context driven.
3. Broader benchmark set is needed for stronger generalization evidence.

## Planned Improvements
1. Add OCR pipeline for scanned reports.
2. Add sentence-level faithfulness scoring.
3. Improve conflict resolution strategy using temporal/context weighting.
4. Add styled DOCX/PDF report export templates.
