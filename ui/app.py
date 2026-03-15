from __future__ import annotations

import json
import sys
import html
import tempfile
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline_runner import run_pipeline


st.set_page_config(
    page_title="DDR Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------------
# UI STYLES
# -------------------------------

def inject_styles() -> None:
    st.markdown(
        """
        <style>

        :root {
            --bg-main:#f5f7f6;
            --bg-card:#ffffff;
            --bg-soft:#f1f6f4;
            --border:#d8e2df;
            --text-main:#0f172a;
            --text-muted:#475569;
            --accent:#0f766e;
            --accent-soft:#e7f5f3;
        }

        .stApp{
            background:var(--bg-main);
            color:var(--text-main);
        }

        [data-testid="stAppViewContainer"] {
            background: var(--bg-main) !important;
            color: var(--text-main) !important;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stStatusWidget"],
        [data-testid="stBottomBlockContainer"] {
            background: var(--bg-main) !important;
        }

        .block-container{
            padding-top:2rem;
            padding-bottom:2rem;
        }

        section[data-testid="stSidebar"]{
            background:#eef4f2;
            border-right:1px solid var(--border);
        }

        section[data-testid="stSidebar"] *{
            color:var(--text-main)!important;
        }

        .hero{
            background:linear-gradient(135deg,#ffffff,#edf6f4);
            border:1px solid var(--border);
            border-radius:16px;
            padding:1.6rem;
            margin-bottom:1.2rem;
            box-shadow:0 8px 18px rgba(0,0,0,0.05);
        }

        .hero h1{
            margin-bottom:0.2rem;
            color:var(--text-main) !important;
        }

        .hero p,
        .hero b,
        .hero .small-note {
            color:var(--text-main) !important;
        }

        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6 {
            color: var(--text-main) !important;
        }

        .card{
            background:var(--bg-card);
            border:1px solid var(--border);
            border-left:5px solid var(--accent);
            border-radius:12px;
            padding:1rem 1.2rem;
            margin-bottom:1rem;
            box-shadow:0 2px 6px rgba(0,0,0,0.05);
            line-height:1.6;
        }

        .section-label{
            font-weight:700;
            margin-bottom:0.3rem;
        }

        .small-note{
            font-size:0.9rem;
            color:var(--text-muted);
        }

        .stButton > button{
            background:var(--accent);
            color:white;
            border-radius:10px;
            border:none;
            padding:0.5rem 1.1rem;
            font-weight:600;
        }

        .stButton > button:hover{
            background:#0b5e57;
        }

        .stButton > button:disabled,
        .stDownloadButton > button:disabled {
            color:#ffffff !important;
            opacity:0.75;
        }

        .stDownloadButton > button,
        button[kind="secondary"],
        button[kind="tertiary"] {
            color:var(--text-main) !important;
            border-color:var(--border) !important;
            background:var(--bg-card) !important;
        }

        .stDownloadButton > button:hover,
        button[kind="secondary"]:hover,
        button[kind="tertiary"]:hover {
            color:var(--text-main) !important;
            background:#eaf2ef !important;
        }

        .stTabs [data-baseweb="tab"]{
            background:var(--bg-soft);
            border-radius:10px;
            border:1px solid var(--border);
            padding:0.4rem 1rem;
            color:var(--text-main) !important;
        }

        .stTabs [aria-selected="true"]{
            background:var(--accent-soft);
            border:1px solid #9ed7d1;
            font-weight:600;
            color:var(--text-main) !important;
        }

        .stTabs [data-baseweb="tab-panel"],
        [data-testid="stVerticalBlock"],
        [data-testid="stExpander"],
        [data-testid="stAlertContainer"] {
            background: transparent !important;
            color: var(--text-main) !important;
        }

        div[data-testid="stFileUploader"] section{
            background:var(--bg-soft);
            border:1px dashed #9fb8b3;
            border-radius:10px;
            padding:1rem;
        }

        div[data-testid="stFileUploader"] * {
            color:var(--text-main) !important;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background:var(--bg-soft) !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] span,
        div[data-testid="stFileUploaderDropzoneInstructions"] small,
        div[data-testid="stFileUploaderFileName"],
        div[data-testid="stFileUploaderFileData"] {
            color:var(--text-main) !important;
            opacity:1 !important;
        }

        div[data-testid="stFileUploader"] button {
            color:var(--text-main) !important;
            background:#ffffff !important;
            border:1px solid var(--border) !important;
        }

        div[data-testid="stFileUploader"] button:hover {
            color:var(--text-main) !important;
            background:#eaf2ef !important;
        }

        [data-testid="stFormSubmitButton"] button,
        [data-testid="baseButton-primary"] {
            color:#ffffff !important;
        }

        pre{
            font-size:0.85rem!important;
        }

        [data-testid="stCodeBlock"] pre,
        [data-testid="stCode"] pre,
        [data-testid="stJson"] pre,
        [data-testid="stJson"] code,
        code {
            background: #f8fbfa !important;
            color: #0f172a !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------
# HELPERS
# -------------------------------

def save_upload(uploaded_file, target_path: Path) -> None:
    target_path.write_bytes(uploaded_file.getbuffer())


def load_artifacts(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_section(title: str, content: str) -> None:
    st.markdown(f"### {title}")
    safe = html.escape(str(content)).replace("\n", "<br><br>")
    st.markdown(f"<div class='card'>{safe}</div>", unsafe_allow_html=True)


# -------------------------------
# AREA OBSERVATIONS
# -------------------------------

def render_area_observations(ddr: dict, image_map: dict[str, str], output_dir: Path):

    st.markdown("### 2. Area-wise Observations")

    for area in ddr.get("area_wise_observations", []):

        st.markdown(
            f"""
            <div class='card'>

            <div class='section-label'>
            {html.escape(area.get("area","Unknown").title())}
            </div>

            <b>Observation</b><br>
            {html.escape(area.get("observation","Not Available"))}

            <br><br>

            <b>Thermal Data</b><br>
            {html.escape(area.get("thermal_data","Not Available"))}

            </div>
            """,
            unsafe_allow_html=True,
        )

        images = area.get("images", [])

        if not images:
            st.info("Image Not Available")
            continue

        cols = st.columns(3)

        for idx, image_id in enumerate(images):

            with cols[idx % 3]:

                if image_id == "Image Not Available":
                    st.info("Image Not Available")
                    continue

                file_path = image_map.get(image_id)

                if file_path and Path(file_path).exists():
                    st.image(file_path, caption=image_id, use_container_width=True)
                    continue

                candidate = Path(image_id)

                if not candidate.is_absolute():
                    candidate = output_dir / candidate

                if candidate.exists():
                    st.image(str(candidate), caption=image_id, use_container_width=True)
                else:
                    st.info("Image Not Available")


# -------------------------------
# RESULTS VIEW
# -------------------------------

def render_results(output_dir: Path):

    report_path = output_dir / "ddr_report.md"
    artifact_path = output_dir / "artifacts.json"

    if not report_path.exists() or not artifact_path.exists():
        st.error("Output files not generated.")
        return

    artifacts = load_artifacts(artifact_path)

    ddr = artifacts.get("ddr", {})
    images = artifacts.get("images", [])

    image_map = {img.get("image_id", ""): img.get("file_path", "") for img in images}

    summary_tab, evidence_tab = st.tabs(["DDR Report", "Evidence & Downloads"])

    with summary_tab:

        left, right = st.columns([2, 1])

        with left:

            render_section(
                "1. Property Issue Summary",
                ddr.get("property_issue_summary", "Not Available"),
            )

            render_area_observations(ddr, image_map, output_dir)

            render_section(
                "3. Probable Root Cause",
                ddr.get("probable_root_cause", "Not Available"),
            )

            render_section(
                "4. Severity Assessment",
                ddr.get("severity_assessment", "Not Available"),
            )

            render_section(
                "5. Recommended Actions",
                ddr.get("recommended_actions", "Not Available"),
            )

            render_section(
                "6. Additional Notes",
                ddr.get("additional_notes", "Not Available"),
            )

            render_section(
                "7. Missing or Unclear Information",
                ddr.get("missing_or_unclear_information", "Not Available"),
            )

        with right:

            st.subheader("Reliability Snapshot")

            col1, col2 = st.columns(2)

            col1.metric("Claims", len(artifacts.get("claims", [])))
            col2.metric("Conflicts", len(artifacts.get("conflicts", [])))

            st.markdown(
                f"""
                <div class='card'>
                <div class='section-label'>Missing Data</div>
                {html.escape(ddr.get("missing_or_unclear_information","None"))}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with evidence_tab:

        st.subheader("Downloads")

        st.download_button(
            "Download DDR Markdown",
            data=report_path.read_text(),
            file_name="ddr_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

        st.download_button(
            "Download Artifacts JSON",
            data=artifact_path.read_text(),
            file_name="artifacts.json",
            mime="application/json",
            use_container_width=True,
        )

        st.subheader("Extracted Claims")
        st.json(artifacts.get("claims", []), expanded=False)

        st.subheader("Detected Conflicts")
        st.json(artifacts.get("conflicts", []), expanded=False)


# -------------------------------
# MAIN APP
# -------------------------------

def main():

    inject_styles()

    st.markdown(
        """
        <div class='hero'>
        <h1>DDR AI Builder</h1>
        <p>
        Upload an <b>Inspection Report</b> and a <b>Thermal Report</b> to generate a
        structured <b>Defect Diagnostic Report (DDR)</b>.
        </p>

        <p class='small-note'>
        Groq-powered claim extraction • Evidence alignment • Conflict detection
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:

        st.header("Run Settings")

        config_path = st.text_input("Config Path", value="config.yaml")

        st.divider()

        st.markdown("### How it works")

        st.caption("1. Upload both reports")
        st.caption("2. Run DDR pipeline")
        st.caption("3. Review structured output")

    col1, col2 = st.columns(2)

    with col1:
        inspection = st.file_uploader("Inspection Report", type=["pdf", "docx"])

    with col2:
        thermal = st.file_uploader("Thermal Report", type=["pdf", "docx"])

    if not inspection or not thermal:
        st.info("Upload both files to enable DDR generation.")

    if st.button("Generate DDR"):

        if not inspection or not thermal:
            st.warning("Please upload both files.")
            return

        with tempfile.TemporaryDirectory(prefix="ddr_ui_") as tmp:

            tmp_dir = Path(tmp)

            input_dir = tmp_dir / "input"
            output_dir = tmp_dir / "output"

            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            inspection_path = input_dir / inspection.name
            thermal_path = input_dir / thermal.name

            save_upload(inspection, inspection_path)
            save_upload(thermal, thermal_path)

            with st.status("Running pipeline...", expanded=True) as status:

                st.write("Ingestion and image extraction")
                st.write("Claim extraction and evidence alignment")
                st.write("Fusion and report generation")

                code = run_pipeline(
                    inspection_path=str(inspection_path),
                    thermal_path=str(thermal_path),
                    output_dir=str(output_dir),
                    config_path=config_path,
                )

                if code != 0:
                    status.update(label="Pipeline failed", state="error")
                    st.error("Pipeline execution failed.")
                    return

                status.update(label="Pipeline completed", state="complete")

            render_results(output_dir)


if __name__ == "__main__":
    main()
