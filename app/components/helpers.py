"""
Shared helper functions for eviStream application
"""
from utils import project_repository as proj_repo
import streamlit as st
import sys
from pathlib import Path

# Setup Python path FIRST - before any local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def load_projects():
    """Load projects from Supabase."""
    projects = proj_repo.list_projects()
    return {"projects": projects}


def get_project(project_id):
    """Return a project with its forms and documents populated."""
    return proj_repo.get_full_project(project_id)


def project_name_exists(name: str) -> bool:
    """Check for duplicate project names."""
    return proj_repo.project_name_exists(name)


def create_project(name, description):
    """Create a new project via Supabase."""
    if project_name_exists(name):
        return None, f"Project '{name}' already exists"

    try:
        row = proj_repo.create_project(name.strip(), description.strip())
        new_project = {
            "id": row.get("id"),
            "name": row.get("name"),
            "description": row.get("description") or "",
            "forms": [],
            "pdfs": [],
        }
        st.session_state.projects_data = {
            "projects": proj_repo.list_projects()
        }
        return new_project, None
    except Exception as e:
        return None, f"Failed to create project: {e}"


def init_session_state():
    """Initialize session state variables."""
    if "projects_data" not in st.session_state:
        st.session_state.projects_data = load_projects()
    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = None
    if "form_fields" not in st.session_state:
        st.session_state.form_fields = []
    if "last_results" not in st.session_state:
        st.session_state.last_results = []
