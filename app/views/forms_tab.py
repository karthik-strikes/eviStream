"""
Forms Tab Content - Modularized (non-Streamlit page module)
"""

import sys
from pathlib import Path
import uuid

import streamlit as st

from core.dspy_generator1 import generate_task_from_form
from core.form_schema_builder import (
    build_field_definition,
    build_form_definition,
    build_form_payload,
)
from core.config import USE_SUPABASE
from utils import project_repository as proj_repo
from components.helpers import save_projects


# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_forms_tab(current_project):
    """Render the Forms tab content."""

    left_col, right_col = st.columns([1.1, 1.2])

    # Existing forms
    with left_col:
        st.markdown(
            '<div class="evi-card"><div class="evi-card-header"><div>'
            '<div class="evi-card-title">Existing forms</div>'
            '<div class="evi-card-subtitle">Forms define the JSON schema your LLM pipeline will produce.</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )

        if current_project["forms"]:
            for form in current_project["forms"]:
                # Prefer new canonical keys but fall back to legacy for older data
                form_name = form.get("form_name") or form.get(
                    "name") or "Untitled form"
                form_description = form.get(
                    "form_description") or form.get("description")

                with st.expander(f"{form_name} · {len(form['fields'])} fields"):
                    if form_description:
                        st.caption(form_description)

                    for field in form["fields"]:
                        field_name = field.get(
                            "field_name") or field.get("name")
                        field_description = field.get(
                            "field_description"
                        ) or field.get("description", "")
                        field_type = field.get(
                            "field_type") or field.get("type", "")
                        st.markdown(
                            f"""
                            <div class="evi-field-pill">
                                <div class="evi-field-pill-main">
                                    <span>{field_name}</span>
                                    <div class="evi-field-pill-desc">{field_description}</div>
                                </div>
                                <div class="evi-field-pill-type">{field_type}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        else:
            st.info(
                "No forms yet. Use the panel on the right to create your first form."
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Create new form
    with right_col:
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

        form_name = st.text_input(
            "Form name",
            placeholder="e.g., Trial Characteristics",
        )
        form_desc = st.text_area(
            "Form description *",
            placeholder="e.g., Extract study design, sample size, setting, and duration from clinical trial papers...",
            height=80,
            help="Required: Describe what this form extracts. This helps the AI understand the context.",
        )

        st.markdown("##### Fields")

        with st.expander("ℹ️ **How form building works**", expanded=False):
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
                        f"📝 Options for {field.get('field_name') or field.get('name')}",
                        expanded=False,
                    ):
                        for opt in field["options"]:
                            st.caption(f"• {opt}")

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
                    "icon": "📝",
                },
                "Number": {
                    "value": "number",
                    "data_type": "number",
                    "desc": "Numeric value only",
                    "example": "Sample size, Age, Duration",
                    "needs_options": False,
                    "icon": "🔢",
                },
                "Dropdown": {
                    "value": "dropdown",
                    "data_type": "text",
                    "desc": "Pick ONE option from a list",
                    "example": "Study type, Funding source",
                    "needs_options": True,
                    "icon": "📋",
                },
                "Checkboxes with Text": {
                    "value": "checkbox_group_with_text",
                    "data_type": "object",
                    "desc": "Multiple selections with values",
                    "example": "Demographics (N, %), Patient data",
                    "needs_options": True,
                    "icon": "☑️",
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
                        {selected_control['icon']} {selected_control['desc']}
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

        with add_c2:
            st.markdown("**What should the AI extract?**")

            smart_defaults = {
                "text": "Describe what information to extract...\n\nExample: What is the study setting? (hospital, community clinic, etc.)",
                "number": "Describe what numeric value to extract...\n\nExample: What is the total number of participants at baseline? Use 'NR' if not reported.",
                "dropdown": "Describe which option to select from the list...\n\nExample: What is the study design? Select from the options below.",
                "checkbox_group_with_text": "Describe what data points to extract for each checkbox field...\n\nExample: Extract all available baseline demographics. Check and fill values for each reported metric. Use 'NR' for not reported.",
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
                        "Each option will have a checkbox ☑️ and a text box for values"
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
                        f"✓ {len(options)} checkbox fields ready", icon="✅")
        else:
            options = None

        add_btn_col, clear_btn_col = st.columns(2)
        with add_btn_col:
            if st.button("Add field", use_container_width=True):
                if not field_name or not field_description:
                    st.error("⚠️ Field name and description are required.")
                elif needs_options and not options:
                    st.error(
                        f"⚠️ {control_display_name} requires at least one option."
                    )
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
                    st.rerun()

        with clear_btn_col:
            if st.button("Clear all fields", use_container_width=True):
                st.session_state.form_fields = []
                st.rerun()

        st.markdown("---")

        if st.button(
            "Generate DSPy task & save form", type="primary", use_container_width=True
        ):
            if not form_name or not st.session_state.form_fields:
                st.error("Form name and at least one field are required.")
            elif not form_desc or not form_desc.strip():
                st.error(
                    "⚠️ Form description is required. Please describe what this form extracts."
                )
            else:
                with st.spinner("Generating DSPy task and schema…"):
                    form_definition = build_form_definition(
                        form_name,
                        form_desc,
                        st.session_state.form_fields,
                    )

                    result = generate_task_from_form(
                        project_id=current_project["id"],
                        form_id=str(uuid.uuid4())[:8],
                        form_data=form_definition,
                    )

                    if result.get("status") == "success":
                        from schemas.registry import refresh_registry

                        refresh_registry()

                        form_payload = build_form_payload(
                            form_name,
                            form_desc,
                            st.session_state.form_fields.copy(),
                            schema_name=result["schema_name"],
                            task_dir=result["task_dir"],
                        )

                        try:
                            if USE_SUPABASE:
                                proj_repo.create_form(
                                    current_project["id"], form_payload
                                )
                            else:
                                current_project.setdefault("forms", []).append(
                                    {
                                        "id": str(uuid.uuid4())[:8],
                                        **form_payload,
                                    }
                                )
                                save_projects(st.session_state.projects_data)

                            st.session_state.form_fields = []
                            st.success(
                                "Form created and registered successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving form: {e}")
                    else:
                        st.error(f"Error: {result.get('error')}")

        st.markdown("</div>", unsafe_allow_html=True)
