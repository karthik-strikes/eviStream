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
                        df = _dict_to_dataframe(res["data"])
                        if df is not None and not df.empty:
                            st.dataframe(
                                df, use_container_width=True, height=400)
                            csv_data = df.to_csv(index=False)
                            st.download_button(
                                "Download CSV",
                                data=csv_data,
                                file_name=f"{Path(res['pdf']).stem}.csv",
                                mime="text/csv",
                                key=f"dl_csv_{res['pdf']}",
                                use_container_width=True,
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
                flattened[key] = json.dumps(value, indent=2)
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
