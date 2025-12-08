"""
Repository layer for projects, forms, and document metadata.

This module centralizes all Supabase access for project-related data and
optionally falls back to the existing projects.json file when Supabase
is not configured.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.config import USE_SUPABASE
from utils.supabase_client import get_supabase_client

PROJECTS_JSON_PATH = Path("storage/database/projects.json")


def _get_supabase_table(table_name: str):
    """Return a Supabase table handle or None if Supabase is not available."""
    if not USE_SUPABASE:
        return None
    client = get_supabase_client()
    if client is None or client.client is None:
        return None
    return client.client.table(table_name)


# -------------------- Fallback JSON helpers -------------------- #

def _load_projects_json() -> Dict[str, Any]:
    """Load the legacy projects.json structure."""
    if not PROJECTS_JSON_PATH.exists():
        return {"projects": []}
    try:
        with PROJECTS_JSON_PATH.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"projects": []}


def _save_projects_json(projects_data: Dict[str, Any]) -> None:
    """Persist the legacy projects.json structure."""
    PROJECTS_JSON_PATH.write_text(json.dumps(projects_data, indent=2))


# -------------------- Projects -------------------- #

def list_projects() -> List[Dict[str, Any]]:
    """
    List all projects.

    When Supabase is enabled, read from the `projects` table.
    Otherwise, fall back to projects.json.
    """
    table = _get_supabase_table("projects")
    if table is None:
        data = _load_projects_json()
        return [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "description": p.get("description"),
            }
            for p in data.get("projects", [])
        ]

    result = table.select("*").order("created_at").execute()
    return result.data or []


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single project by ID (without forms/documents).
    """
    table = _get_supabase_table("projects")
    if table is None:
        data = _load_projects_json()
        for p in data.get("projects", []):
            if p.get("id") == project_id:
                # Return only the top-level fields, forms/docs are handled separately
                return {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "description": p.get("description"),
                }
        return None

    result = (
        table.select("*")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )
    rows = result.data or []
    return rows[0] if rows else None


def create_project(name: str, description: str) -> Dict[str, Any]:
    """
    Create a new project and return the created row.
    """
    table = _get_supabase_table("projects")
    if table is None:
        data = _load_projects_json()
        new_project = {
            "id": name.replace(" ", "_").lower(),  # simple id when offline
            "name": name,
            "description": description,
            "forms": [],
            "pdfs": [],
        }
        data.setdefault("projects", []).append(new_project)
        _save_projects_json(data)
        return {
            "id": new_project["id"],
            "name": new_project["name"],
            "description": new_project["description"],
        }

    payload = {
        "name": name,
        "description": description,
    }
    result = table.insert(payload).execute()
    if not result.data:
        raise RuntimeError("Failed to create project in Supabase.")
    return result.data[0]


def project_name_exists(name: str) -> bool:
    """
    Check if a project with the given name already exists (case-insensitive).
    """
    table = _get_supabase_table("projects")
    if table is None:
        data = _load_projects_json()
        return any(
            (p.get("name") or "").strip().lower() == name.strip().lower()
            for p in data.get("projects", [])
        )

    # Supabase-py supports ilike for case-insensitive matching
    result = (
        table.select("id")
        .ilike("name", name.strip())
        .limit(1)
        .execute()
    )
    rows = result.data or []
    if rows:
        return True

    # Fallback: exact match if ilike is not supported in some environments
    result_eq = (
        table.select("id")
        .eq("name", name.strip())
        .limit(1)
        .execute()
    )
    return bool(result_eq.data)


# -------------------- Forms -------------------- #

def list_forms(project_id: str) -> List[Dict[str, Any]]:
    """
    List all forms for a project.
    """
    table = _get_supabase_table("project_forms")
    # Normalize everything to the new canonical keys:
    #   form_name, form_description, fields, schema_name, task_dir
    if table is None:
        data = _load_projects_json()
        for p in data.get("projects", []):
            if p.get("id") == project_id:
                forms_raw = p.get("forms", [])
                normalized: List[Dict[str, Any]] = []
                for f in forms_raw:
                    normalized.append(
                        {
                            "id": f.get("id"),
                            "form_name": f.get("form_name") or f.get("name"),
                            "form_description": f.get("form_description")
                            or f.get("description"),
                            "fields": f.get("fields") or [],
                            "schema_name": f.get("schema_name"),
                            "task_dir": f.get("task_dir"),
                        }
                    )
                return normalized
        return []

    result = (
        table.select("*")
        .eq("project_id", project_id)
        .order("created_at")
        .execute()
    )
    rows = result.data or []
    normalized: List[Dict[str, Any]] = []
    for row in rows:
        normalized.append(
            {
                "id": row.get("id"),
                "form_name": row.get("name"),
                "form_description": row.get("description"),
                "fields": row.get("fields") or [],
                "schema_name": row.get("schema_name"),
                "task_dir": row.get("task_dir"),
            }
        )
    return normalized


def create_form(project_id: str, form_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a form for a project.

    `form_payload` is expected to contain:
      - name
      - description
      - fields
      - schema_name
      - task_dir
    """
    table = _get_supabase_table("project_forms")
    form_name = form_payload.get("form_name") or form_payload.get("name")
    form_description = form_payload.get("form_description") or form_payload.get(
        "description"
    )

    if table is None:
        data = _load_projects_json()
        for p in data.get("projects", []):
            if p.get("id") == project_id:
                forms = p.setdefault("forms", [])
                # Store using the new canonical keys
                canonical = {
                    "id": form_payload.get("id"),
                    "form_name": form_name,
                    "form_description": form_description,
                    "fields": form_payload.get("fields") or [],
                    "schema_name": form_payload.get("schema_name"),
                    "task_dir": form_payload.get("task_dir"),
                }
                forms.append(canonical)
                _save_projects_json(data)
                return canonical
        raise RuntimeError(f"Project {project_id} not found in projects.json")

    payload = {
        "project_id": project_id,
        # Supabase columns remain name/description but callers use form_name/form_description
        "name": form_name,
        "description": form_description,
        "fields": form_payload.get("fields") or [],
        "schema_name": form_payload.get("schema_name"),
        "task_dir": form_payload.get("task_dir"),
    }
    result = table.insert(payload).execute()
    if not result.data:
        raise RuntimeError("Failed to create form in Supabase.")
    row = result.data[0]
    return {
        "id": row.get("id"),
        "form_name": row.get("name"),
        "form_description": row.get("description"),
        "fields": row.get("fields") or [],
        "schema_name": row.get("schema_name"),
        "task_dir": row.get("task_dir"),
    }


# -------------------- Documents -------------------- #

def list_documents(project_id: str) -> List[Dict[str, Any]]:
    """
    List document metadata for a project.
    """
    table = _get_supabase_table("project_documents")
    if table is None:
        data = _load_projects_json()
        for p in data.get("projects", []):
            if p.get("id") == project_id:
                # Legacy key is "pdfs"
                docs = []
                for d in p.get("pdfs", []):
                    docs.append(
                        {
                            "id": d.get("id"),
                            "filename": d.get("filename"),
                            "unique_filename": d.get("unique_filename"),
                            "markdown_path": None,
                            "pdf_storage_path": d.get("temp_path"),
                            "temp_path": d.get("temp_path"),
                            "markdown_content": d.get("markdown_content"),
                        }
                    )
                return docs
        return []

    result = (
        table.select("*")
        .eq("project_id", project_id)
        .order("created_at")
        .execute()
    )
    rows = result.data or []
    normalized: List[Dict[str, Any]] = []

    for row in rows:
        unique_name = row.get("unique_filename")
        markdown_path = row.get("markdown_path")
        markdown_content: Optional[str] = None

        # Prefer explicit markdown_path if present
        if markdown_path:
            try:
                path_obj = Path(markdown_path)
                if path_obj.exists():
                    data = json.loads(path_obj.read_text())
                    markdown_content = data.get("marker", {}).get("markdown")
            except Exception:
                markdown_content = None

        # Fallback: infer JSON location under output/extracted_pdfs
        if markdown_content is None and unique_name:
            inferred = (
                Path(__file__).parent.parent
                / "output"
                / "extracted_pdfs"
                / unique_name
                / f"{unique_name}.json"
            )
            try:
                if inferred.exists():
                    data = json.loads(inferred.read_text())
                    markdown_content = data.get("marker", {}).get("markdown")
            except Exception:
                markdown_content = None

        normalized.append(
            {
                "id": row.get("id"),
                "filename": row.get("original_filename"),
                "unique_filename": unique_name,
                "markdown_path": markdown_path,
                "pdf_storage_path": row.get("pdf_storage_path"),
                # For backward compatibility, expose temp_path pointing to pdf_storage_path
                "temp_path": row.get("pdf_storage_path"),
                # Make extraction tab work the same in Supabase and local JSON modes
                "markdown_content": markdown_content,
            }
        )

    return normalized


def add_document(project_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add document metadata for a project.

    Expected metadata keys:
      - filename (original filename)
      - unique_filename
      - pdf_storage_path
      - markdown_path
    """
    table = _get_supabase_table("project_documents")
    if table is None:
        data = _load_projects_json()
        for p in data.get("projects", []):
            if p.get("id") == project_id:
                pdfs = p.setdefault("pdfs", [])
                pdf_entry = {
                    "id": metadata.get("id"),
                    "filename": metadata.get("filename"),
                    "unique_filename": metadata.get("unique_filename"),
                    "markdown_content": metadata.get("markdown_content"),
                    "temp_path": metadata.get("pdf_storage_path"),
                }
                pdfs.append(pdf_entry)
                _save_projects_json(data)
                return pdf_entry
        raise RuntimeError(f"Project {project_id} not found in projects.json")

    payload = {
        "project_id": project_id,
        "original_filename": metadata.get("filename"),
        "unique_filename": metadata.get("unique_filename"),
        "pdf_storage_path": metadata.get("pdf_storage_path"),
        "markdown_path": metadata.get("markdown_path"),
    }
    result = table.insert(payload).execute()
    if not result.data:
        raise RuntimeError("Failed to add document metadata in Supabase.")
    row = result.data[0]
    return {
        "id": row.get("id"),
        "filename": row.get("original_filename"),
        "unique_filename": row.get("unique_filename"),
        "markdown_path": row.get("markdown_path"),
        "pdf_storage_path": row.get("pdf_storage_path"),
        "temp_path": row.get("pdf_storage_path"),
    }


# -------------------- Combined helper -------------------- #

def get_full_project(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Convenience helper to return a project with its forms and documents.
    """
    proj = get_project(project_id)
    if proj is None:
        return None
    proj["forms"] = list_forms(project_id)
    proj["pdfs"] = list_documents(project_id)
    return proj
