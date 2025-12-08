"""
Sidebar component for project navigation and creation
"""
import sys
from pathlib import Path

# Setup Python path FIRST - before any local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from components.helpers import create_project, get_project


def render_sidebar():
    """Render the sidebar with project navigation and creation."""

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
                create_btn = st.button(
                    "Create project", use_container_width=True)
            with create_col2:
                reset_btn = st.button("Reset", use_container_width=True)

            if reset_btn:
                st.rerun()

            if create_btn:
                if not new_proj_name.strip():
                    st.error("Project name is required.")
                else:
                    project, error = create_project(
                        new_proj_name, new_proj_desc)
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
