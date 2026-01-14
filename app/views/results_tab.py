"""
Results Tab Content - Modularized (non-Streamlit page module)
"""

import sys
from pathlib import Path
import json

import streamlit as st
import pandas as pd

from components.pdf_viewer import display_pdf_viewer


# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_results_tab():
    """Render the Results tab content."""

    st.markdown(
        """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Latest extraction results</div>
          <div class="evi-card-subtitle">Inspect JSON outputs per PDF and download them for downstream meta-analysis.</div>
      </div>
  </div>
""",
        unsafe_allow_html=True,
    )

    if st.session_state.last_results:
        st.markdown(f"**{len(st.session_state.last_results)} result(s)**")

        for res in st.session_state.last_results:
            with st.expander(res["pdf"], expanded=False):
                cols = st.columns([1.1, 1.4])
                with cols[0]:
                    view_mode = st.radio(
                        "View as:",
                        ["Table", "JSON"],
                        horizontal=True,
                        key=f"view_{res['pdf']}",
                    )

                    if view_mode == "Table":
                        st.markdown("**Extracted Data (Table)**")

                        # Separate subform arrays from regular fields
                        subforms, regular_data = _separate_subforms(
                            res["data"])

                        # Display regular fields first
                        if regular_data:
                            st.markdown("##### Main Fields")
                            df_regular = _dict_to_dataframe(regular_data)
                            if df_regular is not None and not df_regular.empty:
                                st.dataframe(
                                    df_regular, use_container_width=True, height=200)

                        # Display each subform as separate table
                        if subforms:
                            for subform_name, subform_records in subforms.items():
                                st.markdown(
                                    f"##### {subform_name} ({len(subform_records)} records)")
                                df_subform = pd.DataFrame(subform_records)
                                if not df_subform.empty:
                                    st.dataframe(
                                        df_subform, use_container_width=True, height=300)
                                    # Download button for this subform
                                    csv_subform = df_subform.to_csv(
                                        index=False)
                                    st.download_button(
                                        f"Download {subform_name} CSV",
                                        data=csv_subform,
                                        file_name=f"{Path(res['pdf']).stem}_{subform_name}.csv",
                                        mime="text/csv",
                                        key=f"dl_csv_{res['pdf']}_{subform_name}",
                                        use_container_width=True,
                                    )

                        # Download options
                        if regular_data or subforms:
                            st.markdown("---")
                            st.markdown("**Download Options**")

                            col1, col2 = st.columns(2)

                            with col1:
                                # Meta-analysis format (RECOMMENDED for systematic reviews)
                                df_flat = _flatten_to_meta_analysis_format(
                                    res["data"])
                                if df_flat is not None and not df_flat.empty:
                                    csv_flat = df_flat.to_csv(index=False)
                                    st.download_button(
                                        "📊 Meta-Analysis Format (Recommended)",
                                        data=csv_flat,
                                        file_name=f"{Path(res['pdf']).stem}.csv",
                                        mime="text/csv",
                                        key=f"dl_csv_flat_{res['pdf']}",
                                        use_container_width=True,
                                        help="One row per subform record. Ready for RevMan/R/Stata. Study fields repeated on each row."
                                    )

                            with col2:
                                # Hierarchical format (for reference)
                                df_all = _dict_to_dataframe(res["data"])
                                if df_all is not None and not df_all.empty:
                                    csv_all = df_all.to_csv(index=False)
                                    st.download_button(
                                        "📄 Hierarchical Format",
                                        data=csv_all,
                                        file_name=f"{Path(res['pdf']).stem}_hierarchical.csv",
                                        mime="text/csv",
                                        key=f"dl_csv_all_{res['pdf']}",
                                        use_container_width=True,
                                        help="Single row with nested data. For reference only."
                                    )
                        else:
                            st.info(
                                "No data available to display in table format.")
                    else:
                        st.markdown("**Extracted JSON**")
                        st.json(res["data"])
                        st.download_button(
                            "Download JSON",
                            data=json.dumps(res["data"], indent=2),
                            file_name=f"{Path(res['pdf']).stem}.json",
                            mime="application/json",
                            key=f"dl_json_{res['pdf']}",
                            use_container_width=True,
                        )
                with cols[1]:
                    st.markdown("**Source PDF**")
                    if res.get("pdf_path") and Path(res["pdf_path"]).exists():
                        display_pdf_viewer(res["pdf_path"], height=550)
                    else:
                        st.info("No cached PDF available for this run.")
    else:
        st.info("No extraction results yet. Run an extraction in the previous tab.")

    st.markdown("</div>", unsafe_allow_html=True)


def _separate_subforms(data: dict) -> tuple[dict, dict]:
    """
    Separate subform arrays (arrays of objects) from regular fields.

    Returns:
        (subforms_dict, regular_fields_dict)
        - subforms_dict: {field_name: [list of record dicts]}
        - regular_fields_dict: {field_name: value} for non-subform fields
    """
    subforms = {}
    regular = {}

    for key, value in data.items():
        # Check if this is a subform (array of objects)
        if isinstance(value, list) and value and isinstance(value[0], dict):
            subforms[key] = value
        else:
            regular[key] = value

    return subforms, regular


def _flatten_to_meta_analysis_format(data: dict) -> pd.DataFrame:
    """
    Flatten hierarchical data to systematic review format.

    For each subform record, create one row with parent fields repeated.
    This is the standard format for meta-analysis tools (RevMan, Stata, R).

    Example input:
    {
        "study_title": "Sharma 2021",
        "funding": "None",
        "index_tests": [
            {"test_type": "MB", "sensitivity": 0.95},
            {"test_type": "MB+LI", "sensitivity": 1.0}
        ]
    }

    Example output (CSV):
    study_title,funding,test_type,sensitivity
    Sharma 2021,None,MB,0.95
    Sharma 2021,None,MB+LI,1.0
    """
    if not isinstance(data, dict):
        return pd.DataFrame()

    subforms, regular = _separate_subforms(data)

    # If no subforms, return single row with regular fields
    if not subforms:
        flattened = {}
        for key, value in regular.items():
            if isinstance(value, dict):
                # Handle source grounding: extract just the value
                if "value" in value and "source_text" in value:
                    flattened[key] = value.get("value", "")
                else:
                    # Other dicts: flatten with dot notation
                    for nested_key, nested_value in value.items():
                        flattened[f"{key}.{nested_key}"] = _format_value(
                            nested_value)
            else:
                flattened[key] = _format_value(value)
        return pd.DataFrame([flattened])

    # Flatten regular fields (remove source grounding wrapper)
    regular_flat = {}
    for key, value in regular.items():
        if isinstance(value, dict) and "value" in value and "source_text" in value:
            # Source grounding: extract just the value
            regular_flat[key] = value.get("value", "")
        elif isinstance(value, dict):
            # Other dicts: flatten with dot notation
            for nested_key, nested_value in value.items():
                regular_flat[f"{key}.{nested_key}"] = _format_value(
                    nested_value)
        else:
            regular_flat[key] = _format_value(value)

    # Create one row per subform record (cross-product if multiple subforms)
    all_rows = []

    # Get the largest subform to use as primary
    primary_subform_name = max(subforms.keys(), key=lambda k: len(subforms[k]))
    primary_records = subforms[primary_subform_name]
    other_subforms = {k: v for k, v in subforms.items() if k !=
                      primary_subform_name}

    # For each record in primary subform
    for record_idx, record in enumerate(primary_records):
        row = {}

        # Add all regular fields (repeated on each row)
        row.update(regular_flat)

        # Add primary subform fields (flatten nested dicts)
        for field_name, field_value in record.items():
            if isinstance(field_value, dict) and "value" in field_value and "source_text" in field_value:
                # Source grounding: extract just the value
                row[f"{primary_subform_name}.{field_name}"] = field_value.get(
                    "value", "")
            elif isinstance(field_value, dict):
                # Other dicts: flatten
                for nested_key, nested_value in field_value.items():
                    row[f"{primary_subform_name}.{field_name}.{nested_key}"] = _format_value(
                        nested_value)
            elif isinstance(field_value, list):
                # Lists: join as comma-separated
                row[f"{primary_subform_name}.{field_name}"] = ", ".join(
                    str(v) for v in field_value)
            else:
                row[f"{primary_subform_name}.{field_name}"] = _format_value(
                    field_value)

        # Add corresponding records from other subforms (if they exist)
        for subform_name, subform_records in other_subforms.items():
            if record_idx < len(subform_records):
                other_record = subform_records[record_idx]
                for field_name, field_value in other_record.items():
                    if isinstance(field_value, dict) and "value" in field_value and "source_text" in field_value:
                        row[f"{subform_name}.{field_name}"] = field_value.get(
                            "value", "")
                    elif isinstance(field_value, dict):
                        for nested_key, nested_value in field_value.items():
                            row[f"{subform_name}.{field_name}.{nested_key}"] = _format_value(
                                nested_value)
                    elif isinstance(field_value, list):
                        row[f"{subform_name}.{field_name}"] = ", ".join(
                            str(v) for v in field_value)
                    else:
                        row[f"{subform_name}.{field_name}"] = _format_value(
                            field_value)
            else:
                # No corresponding record, leave empty
                row[f"{subform_name}"] = ""

        all_rows.append(row)

    if not all_rows:
        return pd.DataFrame()

    return pd.DataFrame(all_rows)


def _dict_to_dataframe(data: dict) -> pd.DataFrame:
    """Convert a dictionary to a pandas DataFrame, flattening nested structures."""
    if not isinstance(data, dict):
        return pd.DataFrame()

    flattened = {}
    for key, value in data.items():
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                flattened_key = f"{key}.{nested_key}"
                flattened[flattened_key] = _format_value(nested_value)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                # Subform array - show count instead of full JSON
                flattened[key] = f"[{len(value)} records - see separate table below]"
            else:
                flattened[key] = ", ".join(str(v)
                                           for v in value) if value else ""
        else:
            flattened[key] = _format_value(value)

    if not flattened:
        return pd.DataFrame()

    df = pd.DataFrame([flattened])
    return df


def _format_value(value) -> str:
    """Format a value for display in the table."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    return str(value)
