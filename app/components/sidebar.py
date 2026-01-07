"""
Sidebar component for project navigation and creation
"""
from components.helpers import create_project, get_project
import streamlit as st
import sys
from pathlib import Path

# Setup Python path FIRST - before any local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


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

        project_ids = list(project_names.keys())
        select_options = [None] + project_ids
        current_id = st.session_state.get("current_project_id")
        select_index = (
            select_options.index(
                current_id) if current_id in project_names else 0
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
                key="sidebar_new_project_description",
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
