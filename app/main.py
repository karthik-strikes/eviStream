"""
eviStream - Main Streamlit Application
"""

import sys
from pathlib import Path

import streamlit as st

from components.styles import apply_global_styles
from components.helpers import (
    init_session_state,
    get_project,
    create_project,
)
from core.dspy_generator1 import load_dynamic_schemas
from views.documents_tab import render_documents_tab
from views.forms_tab import render_forms_tab
from views.extraction_tab import render_extraction_tab
from views.results_tab import render_results_tab


# Ensure project root is on Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# Load dynamic schemas on startup
load_dynamic_schemas()

# Page Config (do this as early as possible)
st.set_page_config(
    page_title="eviStream · Evidence Extraction Workspace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global styles
apply_global_styles()

# Initialize session state
init_session_state()

# === SIDEBAR: Project navigation ===
with st.sidebar:
    st.markdown('<div class="evi-sidebar-header">Projects</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="evi-sidebar-blurb">Switch between systematic reviews or evidence workspaces.</div>',
        unsafe_allow_html=True,
    )

    project_names = {
        p["id"]: p["name"] for p in st.session_state.projects_data["projects"]
    }

    selected_project_id = st.selectbox(
        "Active project",
        options=list(project_names.keys()) if project_names else [],
        format_func=lambda x: project_names[x],
        index=None if project_names else None,
        placeholder="No project selected",
        label_visibility="collapsed",
    )

    if selected_project_id:
        st.session_state.current_project_id = selected_project_id

    st.markdown('<div class="evi-sidebar-divider"></div>',
                unsafe_allow_html=True)

    with st.expander("Create new project", expanded=not bool(project_names)):
        new_proj_name = st.text_input("Project name")
        new_proj_desc = st.text_area(
            "Short description",
            placeholder="e.g., Oral cancer RCTs · pain outcomes",
            height=70,
        )

        create_col1, create_col2 = st.columns([1.2, 1])
        with create_col1:
            create_btn = st.button("Create project", use_container_width=True)
        with create_col2:
            reset_btn = st.button("Reset", use_container_width=True)

        if reset_btn:
            st.rerun()

        if create_btn:
            if not new_proj_name.strip():
                st.error("Project name is required.")
            else:
                project, error = create_project(new_proj_name, new_proj_desc)
                if error:
                    st.error(error)
                else:
                    st.success("Project created and selected.")
                    st.session_state.current_project_id = project["id"]
                    st.rerun()

    if st.session_state.current_project_id:
        current_project = get_project(st.session_state.current_project_id)
        if current_project:
            st.markdown('<div class="evi-sidebar-divider"></div>',
                        unsafe_allow_html=True)
            st.markdown("#### Snapshot")
            st.markdown(
                '<div class="evi-sidebar-metrics">',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="evi-sidebar-metric-card">
                    <div class="evi-sidebar-metric-label">Forms</div>
                    <div class="evi-sidebar-metric-value">{len(current_project.get("forms", []))}</div>
                </div>
                <div class="evi-sidebar-metric-card">
                    <div class="evi-sidebar-metric-label">Documents</div>
                    <div class="evi-sidebar-metric-value">{len(current_project.get("pdfs", []))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


# === MAIN: Hero Header ===
current_project = (
    get_project(st.session_state.current_project_id)
    if st.session_state.current_project_id
    else None
)

hero_right_steps = """
<div class="evi-hero-steps">
    <div class="evi-step-pill evi-step-pill-active">1. Project & Forms</div>
    <div class="evi-step-pill">2. Upload PDFs</div>
    <div class="evi-step-pill">3. Run Extraction</div>
</div>
"""


# === No Project Selected: Show hero + onboarding ===
if not current_project:
    st.markdown(
        f"""
<div class="evi-hero">
  <div class="evi-hero-left">
    <div class="evi-hero-badge">
        <span>eviStream</span> · Evidence extraction workspace
    </div>
    <h1>Structured data from messy medical PDFs.</h1>
    <p>Design your own extraction forms, process full-text PDFs, and review JSON-ready results — all in one place.</p>
  </div>
  <div>
    {hero_right_steps}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="evi-card">
<div class="evi-card-header">
<div>
<div class="evi-card-title">Getting started</div>
<div class="evi-card-subtitle">
Create your first project from the left sidebar. Then follow the three steps below.
</div>
</div>
</div>

<div class="evi-welcome-grid">

<div class="evi-welcome-card">
<div class="evi-welcome-step">1</div>
<h3>Create a project</h3>
<p>Each project maps to a review (e.g., "Dental pain RCTs") and keeps forms, PDFs, and results together.</p>
</div>

<div class="evi-welcome-card">
<div class="evi-welcome-step">2</div>
<h3>Define extraction forms</h3>
<p>Capture trial characteristics, dichotomous outcomes, continuous outcomes, risk of bias — whatever you need.</p>
</div>

<div class="evi-welcome-card">
<div class="evi-welcome-step">3</div>
<h3>Upload and extract</h3>
<p>Upload PDFs once, then run multiple form-specific extraction pipelines and export JSON.</p>
</div>

</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()


# === Project Header Card ===
st.markdown(
    f"""
<div class="evi-card evi-project-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">{current_project["name"]}</div>
          <div class="evi-card-subtitle">
              {current_project.get("description") or "No description yet. Use this space to describe the question or PICO."}
          </div>
      </div>
      <div class="evi-chip">
          <div class="evi-chip-dot"></div>
          <span>{len(current_project.get("forms", []))} form(s)</span> ·
          <span>{len(current_project.get("pdfs", []))} document(s)</span>
      </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# === Tabs ===
tabs = st.tabs(["Forms", "Documents", "Extraction", "Results"])

# ---------------------- FORMS TAB ---------------------- #
with tabs[0]:
    render_forms_tab(current_project)

# ---------------------- DOCUMENTS TAB ---------------------- #
with tabs[1]:
    render_documents_tab(current_project)

# ---------------------- EXTRACTION TAB ---------------------- #
with tabs[2]:
    render_extraction_tab(current_project)

# ---------------------- RESULTS TAB ---------------------- #
with tabs[3]:
    render_results_tab()
