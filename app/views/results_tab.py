"""
Results Tab Content - Modularized (non-Streamlit page module)
"""

import sys
from pathlib import Path
import json

import streamlit as st

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
                    st.markdown("**Extracted JSON**")
                    st.json(res["data"])
                    st.download_button(
                        "Download JSON",
                        data=json.dumps(res["data"], indent=2),
                        file_name=f"{Path(res['pdf']).stem}.json",
                        mime="application/json",
                        key=f"dl_{res['pdf']}",
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





