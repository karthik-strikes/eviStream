"""
eviStream - Main Streamlit Application
"""

# CRITICAL: Set up Python path FIRST, before any local imports
from views.results_tab import render_results_tab
from views.forms_tab import render_forms_tab
from views.extraction_tab import render_extraction_tab
from views.documents_tab import render_documents_tab
from core.generators import load_dynamic_schemas
from components.styles import apply_global_styles
from components.helpers import create_project, get_project, init_session_state
import streamlit as st
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import everything else


# Load dynamic schemas on startup
load_dynamic_schemas()

# Page Config (do this as early as possible)
st.set_page_config(
    page_title="EviStream · Evidence Extraction Workspace",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global styles
apply_global_styles()

# Initialize session state
init_session_state()

# === SIDEBAR: Project navigation ===
with st.sidebar:
    # Home button at the top
    if st.button("Home", help="Return to home page", use_container_width=True, key="home_btn"):
        st.session_state.current_project_id = None
        st.rerun()

    st.markdown('<div class="evi-sidebar-divider"></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="evi-sidebar-header">Projects</div>',
                unsafe_allow_html=True)

    project_names = {
        p["id"]: p["name"] for p in st.session_state.projects_data["projects"]
    }

    project_ids = list(project_names.keys())
    select_options = [None] + project_ids
    current_id = st.session_state.get("current_project_id")
    select_index = (
        select_options.index(current_id) if current_id in project_names else 0
    )

    selected_project_id = st.selectbox(
        "Active project",
        options=select_options,
        format_func=lambda x: "No project selected"
        if x is None
        else project_names.get(x, str(x)),
        index=select_index,
        label_visibility="collapsed",
        key="active_project_select",
    )

    if selected_project_id is not None:
        st.session_state.current_project_id = selected_project_id

    st.markdown('<div class="evi-sidebar-divider"></div>',
                unsafe_allow_html=True)

    with st.expander("Create new project", expanded=not bool(project_names)):
        new_proj_name = st.text_input("Project name")
        new_proj_desc = st.text_area(
            "Short description",
            placeholder="e.g., Oral cancer RCTs · pain outcomes",
            height=70,
            key="new_project_description",
        )

        create_col1, create_col2 = st.columns([1.5, 1])
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

hero_right_steps = """<div class="evi-hero-steps"><div class="evi-step-pill evi-step-pill-active">1. Project & Forms</div><div class="evi-step-pill">2. Upload PDFs</div><div class="evi-step-pill">3. Run Extraction</div></div>"""


# === No Project Selected: Show hero + onboarding ===
if not current_project:
    total_projects = len(st.session_state.projects_data["projects"])
    # Calculate totals using full project data so forms and documents are counted correctly
    total_forms = 0
    total_docs = 0
    for p in st.session_state.projects_data["projects"]:
        full_project = get_project(p["id"])
        if full_project:
            forms = full_project.get("forms", [])
            pdfs = full_project.get("pdfs", [])
            if isinstance(forms, list):
                total_forms += len(forms)
            if isinstance(pdfs, list):
                total_docs += len(pdfs)

    hero_html = f"""<div class="evi-hero-modern">
<div class="evi-hero-content">
<div class="evi-hero-badge">eviStream · Evidence Extraction</div>
<h1 class="evi-hero-title">Structured Data from<br><span class="highlight-text">Medical Research PDFs</span></h1>
<p class="evi-hero-description">Build custom extraction forms, process clinical trial PDFs with AI, and export structured JSON data for systematic reviews and meta-analysis.</p>
<div class="evi-hero-stats">
<div class="stat-item">
<div class="stat-number">{total_projects}</div>
<div class="stat-label">Projects</div>
</div>
<div class="stat-divider"></div>
<div class="stat-item">
<div class="stat-number">{total_forms}</div>
<div class="stat-label">Forms</div>
</div>
<div class="stat-divider"></div>
<div class="stat-item">
<div class="stat-number">{total_docs}</div>
<div class="stat-label">Documents</div>
</div>
</div>
</div>
</div>"""
    st.markdown(hero_html, unsafe_allow_html=True)

    # Workflow section
    workflow_html = """<div class="workflow-section"><div class="workflow-header"><h2>Workflow</h2><p>Design forms → Upload PDFs → Extract data → Export JSON</p></div><div class="workflow-grid"><div class="workflow-card"><div class="workflow-number">01</div><div class="workflow-content"><h3>Create Project</h3><p>Organize your systematic review work. Each project contains forms, documents, and extracted results.</p></div></div><div class="workflow-card"><div class="workflow-number">02</div><div class="workflow-content"><h3>Build Forms</h3><p>Define extraction fields with text inputs, dropdowns, checkboxes, and numeric fields. Forms are saved and reusable.</p></div></div><div class="workflow-card"><div class="workflow-number">03</div><div class="workflow-content"><h3>Upload PDFs</h3><p>Add clinical trial papers and research documents. PDFs are processed and ready for extraction.</p></div></div><div class="workflow-card"><div class="workflow-number">04</div><div class="workflow-content"><h3>Run Extraction</h3><p>Select a form and document. The AI pipeline extracts data based on your form definitions.</p></div></div><div class="workflow-card"><div class="workflow-number">05</div><div class="workflow-content"><h3>Review Results</h3><p>Validate extracted data, make corrections, and see source context from the original PDF.</p></div></div><div class="workflow-card"><div class="workflow-number">06</div><div class="workflow-content"><h3>Export Data</h3><p>Download structured JSON for analysis, meta-analysis tools, or your data pipeline.</p></div></div></div></div><div class="info-section"><div class="info-grid"><div class="info-item"><strong>DSPy Pipeline</strong><span>Used for structured extraction tasks</span></div><div class="info-item"><strong>Custom Forms</strong><span>Build reusable extraction templates</span></div><div class="info-item"><strong>Batch Processing</strong><span>Process multiple documents efficiently</span></div><div class="info-item"><strong>JSON Export</strong><span>Clean, structured data output</span></div></div></div>"""
    st.markdown(workflow_html, unsafe_allow_html=True)
    st.stop()


# === Project Header Card ===
project_card_html = f"""<div class="evi-card evi-project-card"><div class="evi-card-header"><div><div class="evi-card-title">{current_project["name"]}</div><div class="evi-card-subtitle">{current_project.get("description") or "No description yet. Use this space to describe the question or PICO."}</div></div><div class="evi-chip"><div class="evi-chip-dot"></div><span>{len(current_project.get("forms", []))} form(s)</span> · <span>{len(current_project.get("pdfs", []))} document(s)</span></div></div></div>"""
st.markdown(project_card_html, unsafe_allow_html=True)

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
