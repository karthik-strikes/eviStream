"""
Forms Tab Content - Modularized (non-Streamlit page module)
"""

from utils import project_repository as proj_repo
from core.form_schema_builder import (
    build_field_definition,
    build_form_definition,
    build_form_payload,
)
from core.generators.task_utils import generate_task_from_form
import sys
from pathlib import Path

import streamlit as st

from core.generators import generate_task_from_form

# Add review system imports
from app.components.form_review_ui import render_form_review_interface


# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_forms_tab(current_project):
    """Render the Forms tab content."""

    # Initialize view mode in session state
    if "forms_view_mode" not in st.session_state:
        st.session_state.forms_view_mode = "view"

    # View mode selector
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button(
            "View Existing Forms",
            use_container_width=True,
            type="primary" if st.session_state.forms_view_mode == "view" else "secondary"
        ):
            st.session_state.forms_view_mode = "view"
            st.rerun()

    with col2:
        if st.button(
            "Create New Form",
            use_container_width=True,
            type="primary" if st.session_state.forms_view_mode == "create" else "secondary"
        ):
            st.session_state.forms_view_mode = "create"
            st.rerun()

    # Render based on selected view
    if st.session_state.forms_view_mode == "view":
        render_existing_forms_view(current_project)
    else:
        render_create_form_view(current_project)


def render_existing_forms_view(current_project):
    """Render the existing forms view with review capability."""
    st.markdown(
        '<div class="evi-card"><div class="evi-card-header"><div>'
        '<div class="evi-card-title">Existing forms</div>'
        '<div class="evi-card-subtitle">Forms define the JSON schema your LLM pipeline will produce.</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

    if current_project["forms"]:
        for form in current_project["forms"]:
            # Get form metadata
            form_name = form.get("form_name") or form.get(
                "name") or "Untitled form"
            form_description = form.get(
                "form_description") or form.get("description")
            form_status = form.get("status", "UNKNOWN")

            # Determine status badge and color
            status_info = get_form_status_info(form_status)
            status_badge = status_info["badge"]
            status_color = status_info["color"]

            # Header row with title on left and status pill on right
            header_col1, header_col2 = st.columns([4, 1])
            with header_col1:
                st.markdown(
                    f"**{form_name}** · {len(form['fields'])} fields"
                )
            with header_col2:
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: flex-end;">
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            border-radius: 999px;
                            padding: 0.15rem 0.7rem;
                            font-size: 0.75rem;
                            font-weight: 500;
                            background: {status_color};
                            color: white;
                            white-space: nowrap;
                        ">
                            {status_badge}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Optional description under header
            if form_description:
                st.caption(form_description)

            # Details in a standard expander, closed by default
            with st.expander("View details", expanded=False):
                if form_status == "AWAITING_REVIEW":
                    render_form_review_section(current_project, form)
                elif form_status == "ACTIVE":
                    render_active_form_details(form)
                elif form_status == "GENERATING" or form_status == "REGENERATING":
                    render_generation_progress(form)
                elif form_status == "FAILED":
                    render_failed_form_details(form)
                else:
                    render_standard_form_details(form)

            # Divider between forms can be added here if needed

    else:
        st.info("No forms yet. Click 'Create New Form' to create your first form.")

    st.markdown("</div>", unsafe_allow_html=True)


def get_form_status_info(status: str) -> dict:
    """
    Get status badge and color for a form.

    Args:
        status: Form status

    Returns:
        dict with badge and color
    """
    status_map = {
        "AWAITING_REVIEW": {
            "badge": "Ready for Review",
            "color": "#3b82f6"
        },
        "ACTIVE": {
            "badge": "Active",
            "color": "#10b981"
        },
        "GENERATING": {
            "badge": "Generating...",
            "color": "#f59e0b"
        },
        "REGENERATING": {
            "badge": "Regenerating...",
            "color": "#f59e0b"
        },
        "FAILED": {
            "badge": "Failed",
            "color": "#ef4444"
        },
        "DRAFT": {
            "badge": "Draft",
            "color": "#6b7280"
        }
    }

    return status_map.get(status, {
        "badge": "Processing",
        "color": "#f59e0b"
    })


def render_form_review_section(current_project: dict, form: dict):
    """
    Render the review section for forms awaiting review.

    Args:
        current_project: Current project data
        form: Form data
    """
    from core.generators.form_review_bridge import get_decomposition_service

    project_id = current_project.get("id")
    form_id = form.get("id")

    # Get review data
    service = get_decomposition_service()
    review_data = service.get_review_data(project_id, form_id)

    if not review_data:
        st.error("Could not load review data for this form.")
        return

    # Render the review interface
    render_form_review_interface(project_id, form, review_data)


def render_active_form_details(form: dict):
    """
    Render details for an active form.

    Args:
        form: Form data
    """
    st.success("This form is active and ready to use!")

    # Show task information
    if form.get("schema_name") and form.get("task_dir"):
        st.markdown(
            f"""
            <div style="background: #f0fdf4; padding: 0.5rem; border-radius: 0.4rem; margin-bottom: 1rem; border-left: 3px solid #10b981;">
                <div style="font-size: 0.85rem; color: #065f46;">
                    <strong>Schema:</strong> {form.get('schema_name')}<br>
                    <strong>Task Directory:</strong> {form.get('task_dir')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Show statistics if available
    if form.get("statistics"):
        stats = form["statistics"]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Signatures", stats.get("signatures_generated", 0))
        with col2:
            st.metric("Modules", stats.get("modules_generated", 0))
        with col3:
            st.metric("Pipeline Stages", stats.get("pipeline_stages", 0))

    # Show fields
    st.markdown("**Fields:**")
    for field in form["fields"]:
        field_name = field.get("field_name") or field.get("name")
        field_description = field.get(
            "field_description") or field.get("description", "")
        field_type = field.get("field_type") or field.get("type", "")
        field_options = field.get("options")

        options_badge = ""
        if field_options:
            options_count = len(field_options)
            options_badge = f' <span style="background: #e0ecff; color: #1e3a8a; padding: 0.15rem 0.4rem; border-radius: 999px; font-size: 0.7rem;">{options_count} options</span>'

        st.markdown(
            f"""
            <div class="evi-field-pill">
                <div class="evi-field-pill-main">
                    <span>{field_name}</span>{options_badge}
                    <div class="evi-field-pill-desc">{field_description}</div>
                </div>
                <div class="evi-field-pill-type">{field_type}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if field_options:
            with st.expander(f"View options for '{field_name}'", expanded=False):
                for opt in field_options:
                    st.caption(f"• {opt}")


def render_generation_progress(form: dict):
    """
    Render progress indicator for generating forms.

    Args:
        form: Form data
    """
    status = form.get("status", "GENERATING")

    if status == "REGENERATING":
        st.info("Regenerating form with your feedback...")
        st.markdown("""
        The AI is adjusting the form decomposition based on your feedback.
        This usually takes 1-2 minutes.
        """)
    else:
        st.info("Generating form decomposition...")
        st.markdown("""
        The AI is analyzing your form and creating the extraction workflow.
        This usually takes 1-2 minutes.
        """)

    # Auto-refresh hint
    st.caption("This page will refresh automatically when generation completes.")

    # Manual refresh button
    if st.button("Refresh Status", key=f"refresh_{form.get('id')}"):
        st.rerun()


def render_failed_form_details(form: dict):
    """
    Render error details for failed forms.

    Args:
        form: Form data
    """
    st.error("Form generation failed")

    error = form.get("error", "Unknown error")
    st.markdown(f"**Error:** {error}")

    # Show retry option
    if st.button("Retry Generation", key=f"retry_{form.get('id')}"):
        retry_form_generation(form)


def render_standard_form_details(form: dict):
    """
    Render standard form details (fallback).

    Args:
        form: Form data
    """
    # Show fields
    for field in form["fields"]:
        field_name = field.get("field_name") or field.get("name")
        field_description = field.get(
            "field_description") or field.get("description", "")
        field_type = field.get("field_type") or field.get("type", "")
        field_options = field.get("options")

        options_badge = ""
        if field_options:
            options_count = len(field_options)
            options_badge = f' <span style="background: #e0ecff; color: #1e3a8a; padding: 0.15rem 0.4rem; border-radius: 999px; font-size: 0.7rem;">{options_count} options</span>'

        st.markdown(
            f"""
            <div class="evi-field-pill">
                <div class="evi-field-pill-main">
                    <span>{field_name}</span>{options_badge}
                    <div class="evi-field-pill-desc">{field_description}</div>
                </div>
                <div class="evi-field-pill-type">{field_type}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if field_options:
            with st.expander(f"View options for '{field_name}'", expanded=False):
                for opt in field_options:
                    st.caption(f"• {opt}")


def retry_form_generation(form: dict):
    """
    Retry generation for a failed form.

    Args:
        form: Form data
    """
    st.info("Retrying form generation...")
    # Implementation would trigger regeneration
    # This would call the decomposition service again
    pass


def render_create_form_view(current_project):
    """Render the create new form view."""
    st.markdown(
        """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Create new form</div>
          <div class="evi-card-subtitle">
              Define the fields you want the AI to extract. You can create separate forms for trial characteristics, outcomes, risk of bias, etc.
          </div>
      </div>
  </div>
""",
        unsafe_allow_html=True,
    )

    # Add tabs for different creation methods
    tab1, tab2 = st.tabs(["Build Form", "Import JSON"])

    with tab1:
        render_manual_form_builder(current_project)

    with tab2:
        render_json_import_section(current_project)

    st.markdown("</div>", unsafe_allow_html=True)


def render_manual_form_builder(current_project):
    """Render the manual form building UI."""
    form_name = st.text_input(
        "Form name",
        placeholder="e.g., Trial Characteristics",
    )
    form_desc = st.text_area(
        "Form description *",
        placeholder="e.g., Extract study design, sample size, setting, and duration from clinical trial papers...",
        height=80,
        key="form_description_input",
        help="Required: Describe what this form extracts. This helps the AI understand the context.",
    )

    st.markdown("##### Fields")

    with st.expander("How form building works", expanded=False):
        st.markdown(
            """
        **Step 1:** Add fields to define what data the AI should extract  
        **Step 2:** Each field becomes a form control (text box, dropdown, checkboxes, etc.)  
        **Step 3:** The AI extracts data from PDFs and fills in the form automatically  
        
        **Example:** If you add a "Demographics" field with checkboxes for "Female (N)", "Male (N)", etc.,  
        the AI will read the PDF and extract: `{"Female (N)": {"selected": true, "value": "38"}, ...}`
        """
        )

    # Show current staged fields
    if st.session_state.form_fields:
        for idx, field in enumerate(st.session_state.form_fields):
            col1, col2 = st.columns([5, 1])
            with col1:
                control_friendly_names = {
                    "text": "Text Input",
                    "number": "Number",
                    "dropdown": "Dropdown",
                    "checkbox_group_with_text": "Checkboxes with Text",
                    "subform_table": "Subform/Repeating Table",
                }

                control_type_raw = (
                    field.get("field_control_type")
                    or field.get("control_type")
                    or field.get("field_type")
                    or field.get("type")
                )
                control_display = control_friendly_names.get(
                    control_type_raw, control_type_raw.capitalize()
                )

                options_badge = ""
                if field.get("options"):
                    options_count = len(field["options"])
                    options_badge = f' <span style="background: #e0ecff; color: #1e3a8a; padding: 0.15rem 0.4rem; border-radius: 999px; font-size: 0.7rem;">{options_count} options</span>'
                
                if field.get("subform_fields"):
                    subfields_count = len(field["subform_fields"])
                    options_badge = f' <span style="background: #dbeafe; color: #1e40af; padding: 0.15rem 0.4rem; border-radius: 999px; font-size: 0.7rem;">{subfields_count} subfields</span>'

                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; min-height: 50px;">
                        <div>
                            <div style="font-weight: 600; color: var(--text-main); margin-bottom: 0.2rem;">
                                {field.get('field_name') or field.get('name')} · <span style="font-style: italic; font-weight: 400;">{control_display}</span>{options_badge}
                            </div>
                            <div style="font-size: 0.8rem; color: #6b7280;">
                                {field.get('field_description') or field.get('description', '')}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    '<div style="padding-top: 0.3rem;"></div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Remove", key=f"rm_field_{idx}", use_container_width=True
                ):
                    st.session_state.form_fields.pop(idx)
                    st.rerun()

            if field.get("options"):
                with st.expander(
                    f"Options for {field.get('field_name') or field.get('name')}",
                    expanded=False,
                ):
                    for opt in field["options"]:
                        st.caption(f"• {opt}")
            
            if field.get("subform_fields"):
                with st.expander(
                    f"Subfields for {field.get('field_name') or field.get('name')}",
                    expanded=False,
                ):
                    for subfield in field["subform_fields"]:
                        st.markdown(
                            f"**{subfield.get('field_name')}** ({subfield.get('field_type')})"
                        )
                        st.caption(f"{subfield.get('field_description', '')}")
                        if subfield.get("options"):
                            st.caption(f"Options: {', '.join(subfield['options'])}")
                        st.markdown("---")

            st.markdown("---")
    else:
        st.caption(
            "No fields added yet. Start by adding at least one field below."
        )

    st.markdown("---")

    st.markdown("###### Add field")

    # Field creation
    st.markdown("**Field Name**")
    field_name = st.text_input(
        "Field name",
        placeholder="e.g., study_type, baseline_participants, funding_source",
        key="field_name_input",
        label_visibility="collapsed",
        help="Use lowercase with underscores (e.g., patient_age, study_setting)",
    )

    add_c1, add_c2 = st.columns([1, 1.4])

    with add_c1:
        control_options = {
            "Text Input": {
                "value": "text",
                "data_type": "text",
                "desc": "Free text answer",
                "example": "Study setting, Country, Dates",
                "needs_options": False,
                "needs_subfields": False,
                "icon": "",
            },
            "Number": {
                "value": "number",
                "data_type": "number",
                "desc": "Numeric value only",
                "example": "Sample size, Age, Duration",
                "needs_options": False,
                "needs_subfields": False,
                "icon": "",
            },
            "Dropdown": {
                "value": "dropdown",
                "data_type": "text",
                "desc": "Pick ONE option from a list",
                "example": "Study type, Funding source",
                "needs_options": True,
                "needs_subfields": False,
                "icon": "",
            },
            "Checkboxes with Text": {
                "value": "checkbox_group_with_text",
                "data_type": "object",
                "desc": "Multiple selections with values",
                "example": "Demographics (N, %), Patient data",
                "needs_options": True,
                "needs_subfields": False,
                "icon": "",
            },
            "Subform/Repeating Table": {
                "value": "subform_table",
                "data_type": "array",
                "desc": "Repeating hierarchical data structure",
                "example": "Interventions, Outcomes, Timepoints",
                "needs_options": False,
                "needs_subfields": True,
                "icon": "",
            },
        }

        control_display_name = st.selectbox(
            "Control Type",
            options=list(control_options.keys()),
            key="field_control_type_input",
            help="Choose how this field will appear in the extraction form",
        )

        selected_control = control_options[control_display_name]
        control_type = selected_control["value"]

        # Visual example
        if control_type == "text":
            visual_example = """
            <div style="margin-top: 0.5rem;">
                <input type="text" placeholder="Study setting description..." style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.85rem;" readonly>
            </div>
            """
        elif control_type == "number":
            visual_example = """
            <div style="margin-top: 0.5rem;">
                <input type="number" placeholder="87" style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.85rem;" readonly>
            </div>
            """
        elif control_type == "dropdown":
            visual_example = """
            <div style="margin-top: 0.5rem;">
                <select style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.85rem;">
                    <option>Select an Answer</option>
                    <option>Option 1</option>
                    <option>Option 2</option>
                </select>
            </div>
            """
        elif control_type == "subform_table":
            visual_example = """
            <div style="margin-top: 0.5rem;">
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.85rem;">
                    <thead style="background: #f3f4f6;">
                        <tr>
                            <th style="padding: 0.5rem; text-align: left; border-bottom: 1px solid #d1d5db;">Column 1</th>
                            <th style="padding: 0.5rem; text-align: left; border-bottom: 1px solid #d1d5db;">Column 2</th>
                            <th style="padding: 0.5rem; text-align: left; border-bottom: 1px solid #d1d5db;">Column 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e5e7eb;">Row 1 Value</td>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e5e7eb;">Data</td>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e5e7eb;">Info</td>
                        </tr>
                        <tr>
                            <td style="padding: 0.5rem;">Row 2 Value</td>
                            <td style="padding: 0.5rem;">Data</td>
                            <td style="padding: 0.5rem;">Info</td>
                        </tr>
                    </tbody>
                </table>
                <div style="margin-top: 0.3rem; font-size: 0.75rem; color: #6b7280;">+ Add Row</div>
            </div>
            """
        else:
            visual_example = """
            <div style="margin-top: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem;">
                    <input type="checkbox" style="width: 16px; height: 16px;">
                    <label style="flex: 1; font-size: 0.85rem; margin: 0;">Option 1</label>
                    <input type="text" placeholder="value" style="width: 100px; padding: 0.3rem; border: 1px solid #d1d5db; border-radius: 0.3rem; font-size: 0.8rem;">
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <input type="checkbox" style="width: 16px; height: 16px;">
                    <label style="flex: 1; font-size: 0.85rem; margin: 0;">Option 2</label>
                    <input type="text" placeholder="value" style="width: 100px; padding: 0.3rem; border: 1px solid #d1d5db; border-radius: 0.3rem; font-size: 0.8rem;">
                </div>
            </div>
            """

        st.markdown(
            f"""
            <div style="background: #f0f9ff; padding: 0.7rem; border-radius: 0.5rem; margin-top: 0.5rem; border-left: 3px solid #3b82f6;">
                <div style="font-size: 0.85rem; color: #1e40af; font-weight: 500; margin-bottom: 0.3rem;">
                    {selected_control['desc']}
                </div>
                <div style="font-size: 0.78rem; color: #64748b; margin-bottom: 0.4rem;">
                    Use for: {selected_control['example']}
                </div>
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 500; margin-bottom: 0.3rem;">
                    Visual Example:
                </div>
                {visual_example}
            </div>
            """,
            unsafe_allow_html=True,
        )

        field_type = selected_control["data_type"]
        needs_options = selected_control["needs_options"]
        needs_subfields = selected_control["needs_subfields"]

    with add_c2:
        st.markdown("**What should the AI extract?**")

        smart_defaults = {
            "text": "Describe what information to extract...\n\nExample: What is the study setting? (hospital, community clinic, etc.)",
            "number": "Describe what numeric value to extract...\n\nExample: What is the total number of participants at baseline? Use 'NR' if not reported.",
            "dropdown": "Describe which option to select from the list...\n\nExample: What is the study design? Select from the options below.",
            "checkbox_group_with_text": "Describe what data points to extract for each checkbox field...\n\nExample: Extract all available baseline demographics. Check and fill values for each reported metric. Use 'NR' for not reported.",
            "subform_table": "Describe what repeating data to extract. The AI will find ALL instances and create a table...\n\nExample: Extract all interventions tested in the study. For each intervention, extract name, dosage, and duration.",
        }

        placeholder_text = smart_defaults.get(
            control_type, "Describe what information to extract from the PDF..."
        )

        field_description = st.text_area(
            "Description",
            placeholder=placeholder_text,
            key="field_desc_input",
            height=95,
            label_visibility="collapsed",
            help="Clear instructions help the AI extract more accurate data. Be specific about what to look for.",
        )

    # Advanced options toggle
    with st.expander("**Advanced options** (optional)", expanded=False):
        st.caption("Fine-tune extraction with examples and hints")

        st.markdown("**Example output** (optional)")
        example_value = st.text_input(
            "Example",
            placeholder="e.g., 'Randomized Controlled Trial' or '150' or 'University Hospital'",
            key="field_example_input",
            help="Provide one example of what the extracted value should look like",
            label_visibility="collapsed",
        )

        st.markdown("**Where to look** (optional)")
        extraction_hints = st.text_area(
            "Hints",
            placeholder="e.g., Check Methods section, Look in Table 1, Usually in Abstract",
            height=60,
            key="field_hints_input",
            help="Tell the AI where to find this information in the PDF",
            label_visibility="collapsed",
        )

    # Subform fields section
    if needs_subfields:
        st.markdown("---")
        st.markdown("**Define Subform Fields (Table Columns)**")
        st.caption("Each column represents data to extract for EACH instance found in the document")

        # Initialize session state for subfields
        subfield_key = f"subfields_for_{field_name if field_name else 'new_field'}"
        if subfield_key not in st.session_state:
            st.session_state[subfield_key] = []

        # Show existing subfields
        if st.session_state[subfield_key]:
            st.markdown("**Current Subfields:**")
            for idx, subfield in enumerate(st.session_state[subfield_key]):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{subfield['field_name']}**")
                    st.caption(subfield.get('field_description', ''))
                with col2:
                    st.markdown(f"*{subfield['field_type']}*")
                with col3:
                    if st.button("Remove", key=f"rm_subfield_{subfield_key}_{idx}"):
                        st.session_state[subfield_key].pop(idx)
                        st.rerun()
        else:
            st.info("No subfields defined yet. Add at least one subfield below.")

        # Add subfield form
        st.markdown("---")
        st.markdown("**Add New Subfield:**")

        subcol1, subcol2 = st.columns([1, 1])

        with subcol1:
            subfield_name = st.text_input(
                "Subfield Name",
                placeholder="e.g., intervention_name, dosage, timepoint",
                key=f"subfield_name_input_{subfield_key}",
                help="Name of this column in the repeating table"
            )

            subfield_type = st.selectbox(
                "Data Type",
                options=["text", "number", "enum"],
                key=f"subfield_type_input_{subfield_key}",
                help="Type of data for this column"
            )

        with subcol2:
            subfield_desc = st.text_area(
                "Description",
                placeholder="What should the AI extract for this column?",
                key=f"subfield_desc_input_{subfield_key}",
                height=95,
                help="Clear description helps AI extract accurate data"
            )

        # Subfield options if enum type
        subfield_options = None
        if subfield_type == "enum":
            st.markdown("**Options (for enum type):**")
            subfield_options_text = st.text_area(
                "Options (one per line)",
                placeholder="Option 1\nOption 2\nOption 3",
                key=f"subfield_options_input_{subfield_key}",
                height=80,
                label_visibility="collapsed"
            )
            if subfield_options_text:
                subfield_options = [opt.strip() for opt in subfield_options_text.split("\n") if opt.strip()]

        if st.button("Add Subfield", key=f"add_subfield_btn_{subfield_key}"):
            if not subfield_name or not subfield_desc:
                st.error("Subfield name and description are required")
            else:
                new_subfield = {
                    "field_name": subfield_name.strip(),
                    "field_type": subfield_type,
                    "field_description": subfield_desc.strip()
                }
                if subfield_options:
                    new_subfield["options"] = subfield_options

                st.session_state[subfield_key].append(new_subfield)
                st.success(f"Added subfield: {subfield_name}")
                st.rerun()

        # Preview table structure
        if st.session_state[subfield_key]:
            st.markdown("---")
            st.markdown("**Preview: Table Structure**")
            
            # Build table header
            header_html = "<tr>"
            for subfield in st.session_state[subfield_key]:
                header_html += f"<th style='padding: 0.5rem; text-align: left; border-bottom: 2px solid #d1d5db; background: #f3f4f6;'>{subfield['field_name']}</th>"
            header_html += "</tr>"
            
            # Sample rows
            sample_row = "<tr>"
            for subfield in st.session_state[subfield_key]:
                sample_row += "<td style='padding: 0.5rem; border-bottom: 1px solid #e5e7eb;'>Sample data</td>"
            sample_row += "</tr>"
            
            table_html = f"""
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.85rem; margin-top: 0.5rem;">
                <thead>{header_html}</thead>
                <tbody>{sample_row}{sample_row}</tbody>
            </table>
            <div style="margin-top: 0.3rem; font-size: 0.75rem; color: #6b7280;">AI will extract multiple rows, one for each instance found</div>
            """
            st.markdown(table_html, unsafe_allow_html=True)

    # Options section
    if needs_options:
        st.markdown("---")

        if control_type == "dropdown":
            st.markdown("**Define Dropdown Options**")

            col_label, col_smart = st.columns([3, 2])
            with col_label:
                st.caption("Users will select ONE option from this list")
            with col_smart:
                auto_add_nr = st.checkbox(
                    "Auto-add 'Not reported'",
                    value=True,
                    key="auto_nr_dropdown",
                    help="Automatically include 'Not reported' as an option",
                )

            placeholder_text = (
                "Yes\nNo" if auto_add_nr else "Yes\nNo\nNot reported"
            )
            options_text = st.text_area(
                "Options (one per line)",
                placeholder=placeholder_text,
                key="field_options_input",
                height=100,
                label_visibility="collapsed",
            )
            options = [
                opt.strip() for opt in options_text.split("\n") if opt.strip()
            ]

            if auto_add_nr and "Not reported" not in options and "not reported" not in [
                o.lower() for o in options
            ]:
                options.append("Not reported")

            if options:
                st.markdown("**Preview:**")
                st.markdown(
                    f"""
                    <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 0.5rem; padding: 0.7rem; margin-top: 0.5rem;">
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 0.3rem;">Dropdown will show:</div>
                        <select style="width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 0.4rem; font-size: 0.9rem;">
                            <option>Select an Answer</option>
                            {''.join([f'<option>{opt}</option>' for opt in options])}
                        </select>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:  # checkbox_group_with_text
            st.markdown("**Define Checkbox Fields**")

            col_label, col_smart = st.columns([3, 2])
            with col_label:
                st.caption(
                    "Each option will have a checkbox and a text box for values"
                )
            with col_smart:
                auto_format_names = st.checkbox(
                    "Auto-format names",
                    value=True,
                    key="auto_format_checkbox",
                    help="Automatically clean up field names (e.g., add spacing, proper case)",
                )

            placeholder_text = "Total initial patients recruited (N)\nFemale (N)\nFemale (%)\nMale (N)\nMale (%)"
            options_text = st.text_area(
                "Options (one per line)",
                placeholder=placeholder_text,
                key="field_options_input",
                height=120,
                label_visibility="collapsed",
            )
            raw_options = [
                opt.strip() for opt in options_text.split("\n") if opt.strip()
            ]

            if auto_format_names:
                options = []
                for opt in raw_options:
                    formatted = opt[0].upper() + opt[1:] if opt else opt
                    options.append(formatted)
            else:
                options = raw_options

            if options:
                st.markdown(
                    "**Preview:** _This is what the form will look like_"
                )
                st.markdown(
                    """
                    <div style="background: #f9fafb; border: 2px dashed #d1d5db; border-radius: 0.5rem; padding: 1rem; margin-top: 0.5rem;">
                    """,
                    unsafe_allow_html=True,
                )

                for opt in options:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.6rem; padding: 0.4rem; background: white; border-radius: 0.3rem; border: 1px solid #e5e7eb;">
                            <input type="checkbox" style="width: 18px; height: 18px; cursor: pointer;">
                            <label style="flex: 1; font-size: 0.9rem; color: #374151; margin: 0;">{opt}</label>
                            <input type="text" placeholder="" style="width: 150px; padding: 0.4rem; border: 1px solid #d1d5db; border-radius: 0.3rem; font-size: 0.85rem;">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)
                st.success(
                    f"{len(options)} checkbox fields ready")
    else:
        options = None

    add_btn_col, clear_btn_col = st.columns(2)
    with add_btn_col:
        if st.button("Add field", use_container_width=True):
            if not field_name or not field_description:
                st.error("Field name and description are required.")
            elif needs_options and not options:
                st.error(
                    f"{control_display_name} requires at least one option."
                )
            elif needs_subfields:
                # Validate subform fields
                subfield_key = f"subfields_for_{field_name if field_name else 'new_field'}"
                subform_fields = st.session_state.get(subfield_key, [])
                
                if not subform_fields:
                    st.error("Subform requires at least one subfield. Add subfields above.")
                else:
                    new_field = build_field_definition(
                        name=field_name,
                        data_type=field_type,
                        control_type=control_type,
                        description=field_description,
                        options=None,
                        example=example_value if "example_value" in locals() else None,
                        extraction_hints=extraction_hints if "extraction_hints" in locals() else None,
                        subform_fields=subform_fields,
                    )

                    st.session_state.form_fields.append(new_field)
                    
                    # Clear subfields from session state
                    if subfield_key in st.session_state:
                        del st.session_state[subfield_key]
                    
                    st.success(f"Added subform field '{field_name}' with {len(subform_fields)} subfields")
            else:
                new_field = build_field_definition(
                    name=field_name,
                    data_type=field_type,
                    control_type=control_type,
                    description=field_description,
                    options=options,
                    example=example_value if "example_value" in locals() else None,
                    extraction_hints=extraction_hints
                    if "extraction_hints" in locals()
                    else None,
                )

                st.session_state.form_fields.append(new_field)

                # Clear form input values from session state to reset the form
                keys_to_clear = [
                    "field_name_input",
                    "field_desc_input",
                    "field_control_type_input",
                    "field_options_input",
                    "field_example_input",
                    "field_hints_input",
                    "auto_nr_dropdown",
                    "auto_format_checkbox",
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

                st.rerun()

    with clear_btn_col:
        if st.button("Clear all fields", use_container_width=True):
            st.session_state.form_fields = []

            # Also clear form input values
            keys_to_clear = [
                "field_name_input",
                "field_desc_input",
                "field_control_type_input",
                "field_options_input",
                "field_example_input",
                "field_hints_input",
                "auto_nr_dropdown",
                "auto_format_checkbox",
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

    st.markdown("---")

    # Human-in-the-loop toggle
    enable_review = st.checkbox(
        "Enable Human Review",
        value=True,
        key="enable_review_manual_form",
        help="If enabled, form decomposition will pause for your review before generating code. If disabled, code will be generated automatically."
    )

    # Save Form with review workflow integration
    if st.button("Save Form", type="primary", use_container_width=True):
        if not form_name or not st.session_state.form_fields:
            st.error("Form name and at least one field are required.")
        elif not form_desc or not form_desc.strip():
            st.error(
                "Form description is required. Please describe what this form extracts."
            )
        else:
            # Build form definition
            form_definition = build_form_definition(
                form_name,
                form_desc,
                st.session_state.form_fields,
            )

            # Create initial form payload
            initial_form_payload = {
                "form_name": form_name,
                "form_description": form_desc,
                "fields": st.session_state.form_fields.copy(),
                "status": "DRAFT",  # Initial status
                "schema_name": None,
                "task_dir": None,
            }

            try:
                # Save form to database
                with st.spinner("Saving form..."):
                    saved_form = proj_repo.create_form(
                        current_project["id"],
                        initial_form_payload
                    )
                    saved_form_id = saved_form.get("id")

                st.success("Form saved.")

                # Start decomposition workflow
                with st.spinner("Starting form decomposition..."):
                    from core.generators.form_review_bridge import get_decomposition_service
                    service = get_decomposition_service()
                    result = service.start_decomposition(
                        project_id=current_project["id"],
                        form_id=saved_form_id,
                        form_data=form_definition,
                        enable_review=enable_review
                    )

                if result.get("success"):
                    if result.get("status") == "awaiting_review":
                        st.success("Form decomposition ready for review.")
                        st.info(
                            "Check the 'View Existing Forms' tab to review your form.")
                    elif result.get("status") == "completed":
                        st.success(
                            "Form created and code generated successfully.")
                        st.balloons()
                        st.info(
                            "Form is now active. You can start using it for extraction.")
                    else:
                        st.success("Form created and activated.")
                else:
                    st.error(f"Decomposition failed: {result.get('error')}")

                    if result.get("errors"):
                        with st.expander("Show errors"):
                            for error in result.get("errors", []):
                                st.error(error)

                # Clear form fields
                st.session_state.form_fields = []
                st.rerun()

            except Exception as e:
                import traceback
                st.error(f"Error: {e}")
                with st.expander("Show details"):
                    st.code(traceback.format_exc())


def render_json_import_section(current_project):
    """Render JSON import section within Create Form tab."""
    import json
    import uuid

    st.markdown("##### Import from JSON")
    st.caption("Paste JSON or upload a file to quickly create a form")

    # Add input method selector
    method = st.radio("Choose input method:", [
                      "Paste JSON", "Upload File", "Use Example"], horizontal=True, label_visibility="collapsed")

    # Human-in-the-loop toggle for JSON import
    enable_review_json = st.checkbox(
        "Enable Human Review",
        value=True,
        key="enable_review_json_import",
        help="If enabled, form decomposition will pause for your review before generating code."
    )

    if method == "Paste JSON":
        # Pre-fill with template if selected
        default_value = st.session_state.get("json_template", "")
        if default_value:
            st.session_state.pop("json_template")

        json_text = st.text_area(
            "Form JSON",
            value=default_value,
            height=250,
            placeholder='{"form_name": "...", "form_description": "...", "fields": [...]}',
            help="Paste your form definition in JSON format",
            key="json_import_quick_text"
        )

        # Preview
        if json_text:
            try:
                form_data = json.loads(json_text)
                with st.expander("Preview", expanded=False):
                    st.json(form_data)
            except:
                st.warning("Invalid JSON")

        if st.button("Save Form", type="primary", disabled=not json_text):
            try:
                form_data = json.loads(json_text)
                _process_json_import(
                    current_project, form_data, enable_review_json)
            except Exception as e:
                st.error(f"Error: {e}")

    elif method == "Upload File":
        uploaded_file = st.file_uploader("Choose JSON file", type=["json"])

        if uploaded_file:
            try:
                file_content = uploaded_file.read().decode("utf-8")
                form_data = json.loads(file_content)

                st.success(f"File loaded: {uploaded_file.name}")
                with st.expander("Preview"):
                    st.json(form_data)

                if st.button("Save Form", type="primary"):
                    _process_json_import(
                        current_project, form_data, enable_review_json)
            except Exception as e:
                st.error(f"Error: {e}")

    else:  # Use Example
        st.markdown("**Example templates:**")

        example_simple = {
            "form_name": "Simple Patient Info",
            "form_description": "Extract basic patient information",
            "fields": [
                {"field_name": "patient_age", "type": "number",
                    "field_description": "Age in years"},
                {"field_name": "diagnosis", "type": "text",
                    "field_description": "Primary diagnosis"}
            ]
        }

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Simple Example"):
                st.json(example_simple)
                if st.button("Use Simple Template"):
                    st.session_state.json_template = json.dumps(
                        example_simple, indent=2)
                    st.rerun()

        with col2:
            st.info(
                "Check `test_form_simple.json` in project root for more examples.")


def _process_json_import(current_project, form_data, enable_review=True):
    """Process JSON import with same workflow as manual form builder."""
    if "form_name" not in form_data:
        st.error("JSON must have 'form_name' field")
        return

    if "fields" not in form_data or not form_data["fields"]:
        st.error("JSON must have 'fields' array with at least one field")
        return

    # Create initial form payload (same as manual form builder)
    initial_form_payload = {
        "form_name": form_data.get("form_name"),
        "form_description": form_data.get("form_description", ""),
        "fields": form_data.get("fields", []),
        "status": "DRAFT",
        "schema_name": None,
        "task_dir": None,
    }

    try:
        # Save form to database
        with st.spinner("Saving form..."):
            saved_form = proj_repo.create_form(
                current_project["id"],
                initial_form_payload
            )
            saved_form_id = saved_form.get("id")

        st.success("Form saved.")

        # Start decomposition workflow (same as manual form builder)
        with st.spinner("Starting form decomposition..."):
            from core.generators.form_review_bridge import get_decomposition_service
            service = get_decomposition_service()
            result = service.start_decomposition(
                project_id=current_project["id"],
                form_id=saved_form_id,
                form_data=form_data,
                enable_review=enable_review
            )

        if result.get("success"):
            if result.get("status") == "awaiting_review":
                st.success("Form decomposition ready for review.")
                st.info("Check the 'View Existing Forms' tab to review your form.")
            elif result.get("status") == "completed":
                st.success("Form created and code generated successfully.")
                st.balloons()
                st.info(
                    "Form is now active. You can start using it for extraction.")
            else:
                st.success("Form created and activated.")
        else:
            st.error(f"Decomposition failed: {result.get('error')}")

            if result.get("errors"):
                with st.expander("Show errors"):
                    for error in result.get("errors", []):
                        st.error(error)

        # Switch to view mode to see the form
        st.session_state.forms_view_mode = "view"
        st.rerun()

    except Exception as e:
        import traceback
        st.error(f"Error: {e}")
        with st.expander("Show details"):
            st.code(traceback.format_exc())


def render_import_json_view(current_project):
    """Render JSON import view for quick testing."""
    import json
    import uuid

    st.markdown(
        """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Import form from JSON</div>
          <div class="evi-card-subtitle">
              Paste or upload a JSON file to quickly import form definitions for testing.
          </div>
      </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Add tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["Paste JSON", "Upload File", "Examples"])

    with tab1:
        st.markdown("##### Paste your form JSON below:")

        # Pre-fill with template if selected from examples tab
        default_value = st.session_state.get("json_template", "")
        if default_value:
            st.session_state.pop("json_template")  # Clear after use

        json_text = st.text_area(
            "Form JSON",
            value=default_value,
            height=300,
            placeholder='''{
  "form_name": "Example Form",
  "form_description": "Description here...",
  "fields": [
    {
      "field_name": "field1",
      "type": "text",
      "field_description": "Description...",
      "example": "Example value"
    }
  ]
}''',
            label_visibility="collapsed",
            key="json_import_full_text"
        )

        # Validate and preview JSON
        if json_text:
            try:
                form_data = json.loads(json_text)

                # Show preview
                with st.expander("Preview", expanded=True):
                    st.markdown(
                        f"**Form Name:** {form_data.get('form_name', 'Not specified')}")
                    st.markdown(
                        f"**Description:** {form_data.get('form_description', 'Not specified')}")
                    st.markdown(
                        f"**Fields:** {len(form_data.get('fields', []))} fields")

                    if form_data.get('fields'):
                        st.markdown("**Field names:**")
                        for field in form_data.get('fields', []):
                            field_name = field.get('field_name', 'unnamed')
                            field_type = field.get('type', 'unknown')
                            st.caption(f"  • {field_name} ({field_type})")
            except json.JSONDecodeError as e:
                st.warning(f"JSON validation error: {e}")

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Import JSON", type="primary", use_container_width=True):
                try:
                    form_data = json.loads(json_text)
                    _process_json_import(current_project, form_data)
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")
                except Exception as e:
                    import traceback
                    st.error(f"Error: {e}")
                    with st.expander("Show full error"):
                        st.code(traceback.format_exc())

    with tab2:
        st.markdown("##### Upload a JSON file:")
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=["json"],
            help="Upload a .json file containing your form definition",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            try:
                file_content = uploaded_file.read().decode("utf-8")
                form_data = json.loads(file_content)

                st.success(f"File loaded: {uploaded_file.name}")
                st.json(form_data)

                if st.button("Import from uploaded file", type="primary"):
                    _process_json_import(current_project, form_data)

            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON file: {e}")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with tab3:
        st.markdown("##### Example JSON templates:")

        example_simple = {
            "form_name": "Simple Patient Info",
            "form_description": "Extract basic patient information",
            "fields": [
                {
                    "field_name": "patient_age",
                    "type": "number",
                    "field_description": "Age in years",
                    "example": "45"
                },
                {
                    "field_name": "diagnosis",
                    "type": "text",
                    "field_description": "Primary diagnosis",
                    "example": "Type 2 Diabetes"
                }
            ]
        }

        with st.expander("Simple Form Example", expanded=True):
            st.json(example_simple)
            if st.button("Use this template", key="use_simple"):
                st.session_state.json_template = json.dumps(
                    example_simple, indent=2)
                st.rerun()

        # Add more comprehensive example
        example_detailed = {
            "form_name": "Clinical Trial Characteristics",
            "form_description": "Extract study design, sample size, and key characteristics from clinical trials",
            "fields": [
                {
                    "field_name": "study_design",
                    "type": "enum",
                    "field_description": "Type of study design",
                    "options": ["RCT", "cohort", "case_control", "cross_sectional"],
                    "example": "RCT",
                    "extraction_hints": "Look in methods or abstract"
                },
                {
                    "field_name": "sample_size",
                    "type": "number",
                    "field_description": "Total number of participants",
                    "example": "120",
                    "extraction_hints": "May be stated as n= or 'patients enrolled'"
                },
                {
                    "field_name": "primary_outcome",
                    "type": "text",
                    "field_description": "Primary outcome measure",
                    "example": "Change in HbA1c at 12 weeks",
                    "extraction_hints": "Explicitly stated in methods section"
                },
                {
                    "field_name": "outcome_significant",
                    "type": "enum",
                    "field_description": "Was primary outcome statistically significant?",
                    "depends_on": ["primary_outcome"],
                    "options": ["yes", "no", "not_reported"],
                    "example": "yes",
                    "extraction_hints": "Look for p-values < 0.05"
                }
            ]
        }

        with st.expander("Clinical Trial Example", expanded=False):
            st.json(example_detailed)
            if st.button("Use this template", key="use_detailed"):
                st.session_state.json_template = json.dumps(
                    example_detailed, indent=2)
                st.rerun()

        st.markdown("---")
        st.markdown(
            "**Tip:** Check `test_form_simple.json` and `test_form_dental_implant.json` in the project root for more examples!")

    st.markdown("</div>", unsafe_allow_html=True)


def update_form_with_task(project_id: str, form_id: str, schema_name: str, task_dir: str):
    """Update a form with generated task information."""
    from utils.supabase_client import get_supabase_client

    client = get_supabase_client()
    if client and client.client:
        client.client.table("project_forms").update({
            "schema_name": schema_name,
            "task_dir": task_dir
        }).eq("id", form_id).eq("project_id", project_id).execute()
