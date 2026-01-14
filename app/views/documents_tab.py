"""
Documents Tab Content - Modularized (non-Streamlit page module)
"""

import sys
from pathlib import Path

import streamlit as st

from components.pdf_viewer import display_pdf_viewer
from utils import project_repository as proj_repo


# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def render_documents_tab(current_project):
    """Render the Documents tab content."""

    upload_col, list_col = st.columns([1.1, 1.3])

    # --- Upload PDFs ---
    with upload_col:
        st.markdown(
            """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Upload PDFs</div>
          <div class="evi-card-subtitle">Upload full-text PDFs once. eviStream will convert them to markdown for extraction.</div>
      </div>
  </div>
""",
            unsafe_allow_html=True,
        )

        uploaded_files = st.file_uploader(
            "Select PDF files",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.caption(
                f"{len(uploaded_files)} file(s) selected. They will be cached inside this project after processing."
            )
            if st.button(
                f"Process {len(uploaded_files)} PDF(s)",
                type="primary",
                use_container_width=True,
            ):
                from pdf_processor.streamlit_wrapper import StreamlitPDFProcessor

                processor = StreamlitPDFProcessor()
                progress = st.progress(0)
                status = st.empty()

                processed = 0
                for idx, file in enumerate(uploaded_files):
                    status.info(f"Processing {file.name}…")
                    try:
                        result = processor.process_uploaded_file(file)
                        if result.get("status") == "success":
                            temp_dir = Path("storage/uploads/pdfs")
                            temp_dir.mkdir(parents=True, exist_ok=True)
                            temp_path = temp_dir / file.name
                            with open(temp_path, "wb") as f:
                                f.write(file.getbuffer())

                            try:
                                unique_name = result.get("unique_filename")
                                markdown_json_path = (
                                    Path(processor.output_dir)
                                    / unique_name
                                    / f"{unique_name}.json"
                                )
                                proj_repo.add_document(
                                    current_project["id"],
                                    {
                                        "filename": file.name,
                                        "unique_filename": unique_name,
                                        "pdf_storage_path": str(temp_path),
                                        "markdown_path": str(markdown_json_path),
                                    },
                                )
                                processed += 1
                            except Exception as e:
                                st.warning(
                                    f"Could not save metadata for {file.name}: {e}"
                                )
                    except Exception as e:
                        st.warning(f"Could not process {file.name}: {e}")

                    progress.progress((idx + 1) / len(uploaded_files))

                status.success(f"Processed {processed} PDF(s).")
                st.rerun()

        else:
            st.caption("No files selected yet.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Document Library ---
    with list_col:
        st.markdown(
            """
<div class="evi-card">
  <div class="evi-card-header">
      <div>
          <div class="evi-card-title">Document library</div>
          <div class="evi-card-subtitle">All PDFs attached to this project. Use them for extraction in the next step.</div>
      </div>
  </div>
""",
            unsafe_allow_html=True,
        )

        if current_project["pdfs"]:
            st.markdown(f"**{len(current_project['pdfs'])} document(s)**")
            for pdf in current_project["pdfs"]:
                with st.expander(pdf["filename"]):
                    cols = st.columns([1, 2])
                    with cols[0]:
                        st.caption(f"Internal ID: `{pdf['id']}`")
                        if st.button(
                            "View PDF",
                            key=f"view_{pdf['id']}",
                            use_container_width=True,
                        ):
                            if pdf.get("temp_path") and Path(pdf["temp_path"]).exists():
                                display_pdf_viewer(
                                    pdf["temp_path"], height=600)
                            else:
                                st.warning("Cached PDF path not found.")
                    with cols[1]:
                        st.caption("Markdown snapshot (first 600 chars):")
                        md_preview = (pdf.get("markdown_content") or "")[:600]
                        st.code(
                            md_preview or "[No markdown content cached yet]",
                            language="markdown",
                        )
        else:
            st.info("No PDFs uploaded for this project yet.")

        st.markdown("</div>", unsafe_allow_html=True)
