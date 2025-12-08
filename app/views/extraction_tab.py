"""
Extraction Tab Content - Modularized (non-Streamlit page module)
"""

import sys
from pathlib import Path
import inspect
import asyncio

import streamlit as st


# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_extraction_tab(current_project):
    """Render the Extraction tab content."""

    st.markdown(
        """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Run extraction</div>
          <div class="evi-card-subtitle">
              Choose a form (schema) and one or more PDFs. eviStream will run the DSPy pipeline and return structured JSON.
          </div>
      </div>
  </div>
""",
        unsafe_allow_html=True,
    )

    if not current_project["forms"] or not current_project["pdfs"]:
        st.warning(
            "You need at least one form and one uploaded PDF to run extraction."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    from schemas.registry import get_schema

    sel_col1, sel_col2 = st.columns([1, 1.3])

    with sel_col1:
        # Prefer new canonical key form_name, fall back to legacy name for old data
        form_names = [
            f.get("form_name") or f.get("name") or "Untitled form"
            for f in current_project["forms"]
        ]
        selected_form_name = st.selectbox("Form", form_names)
        selected_form = next(
            f
            for f in current_project["forms"]
            if (f.get("form_name") or f.get("name")) == selected_form_name
        )

    with sel_col2:
        pdf_names = [p["filename"] for p in current_project["pdfs"]]
        selected_pdf_names = st.multiselect(
            "PDFs to extract from",
            pdf_names,
            default=pdf_names,
        )
        selected_pdfs = [
            p for p in current_project["pdfs"] if p["filename"] in selected_pdf_names
        ]

    st.markdown("---")

    if st.button("Run extraction", type="primary", use_container_width=True):
        if not selected_pdfs:
            st.error("Please select at least one PDF.")
        else:
            progress = st.progress(0)
            status = st.empty()

            try:
                schema_def = get_schema(selected_form["schema_name"])
                pipeline = schema_def.pipeline_factory()
                results = []

                for i, pdf in enumerate(selected_pdfs):
                    status.info(f"Extracting from: {pdf['filename']}…")

                    if pdf.get("markdown_content"):
                        maybe_coro = pipeline(pdf["markdown_content"])
                        if inspect.isawaitable(maybe_coro):
                            result = asyncio.run(maybe_coro)
                        else:
                            result = maybe_coro
                        data = {k: v for k, v in result.items() if not k.startswith("_")}
                        results.append(
                            {
                                "pdf": pdf["filename"],
                                "pdf_path": pdf.get("temp_path"),
                                "data": data,
                            }
                        )

                    progress.progress((i + 1) / len(selected_pdfs))

                st.session_state.last_results = results
                status.success("Extraction complete.")
                st.success(f"Extracted data from {len(results)} document(s).")
            except Exception as e:
                st.error(f"Error during extraction: {e}")

    st.markdown("</div>", unsafe_allow_html=True)





