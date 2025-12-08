"""
Shared helper functions for eviStream application
"""
import sys
from pathlib import Path

# Setup Python path FIRST - before any local imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import uuid
import json

from utils import project_repository as proj_repo
from core.config import USE_SUPABASE


# Constants
PROJECTS_FILE = "storage/database/projects.json"


def load_projects():
    """
    Load projects either from Supabase (preferred) or from the local
    projects.json file as a fallback.
    """
    if USE_SUPABASE:
        try:
            projects = proj_repo.list_projects()
            return {"projects": projects}
        except Exception:
            pass

    if not Path(PROJECTS_FILE).exists():
        return {"projects": []}
    try:
        with open(PROJECTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"projects": []}


def save_projects(projects_data):
    """Persist projects to projects.json."""
    with open(PROJECTS_FILE, "w") as f:
        json.dump(projects_data, f, indent=2)


def get_project(project_id):
    """Return a project with its forms and documents populated."""
    if USE_SUPABASE:
        try:
            return proj_repo.get_full_project(project_id)
        except Exception:
            return None

    for p in st.session_state.projects_data["projects"]:
        if p["id"] == project_id:
            return p
    return None


def project_name_exists(name: str) -> bool:
    """Check for duplicate project names."""
    if USE_SUPABASE:
        try:
            return proj_repo.project_name_exists(name)
        except Exception:
            pass

    return any(
        p["name"].strip().lower() == name.strip().lower()
        for p in st.session_state.projects_data["projects"]
    )


def create_project(name, description):
    """Create a new project via Supabase or the legacy JSON path."""
    if project_name_exists(name):
        return None, f"Project '{name}' already exists"

    if USE_SUPABASE:
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
            return None, f"Failed to create project in Supabase: {e}"

    new_project = {
        "id": str(uuid.uuid4())[:8],
        "name": name.strip(),
        "description": description.strip(),
        "forms": [],
        "pdfs": [],
    }
    st.session_state.projects_data["projects"].append(new_project)
    save_projects(st.session_state.projects_data)
    return new_project, None


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
